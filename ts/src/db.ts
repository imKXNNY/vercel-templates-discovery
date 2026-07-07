import Database from "better-sqlite3";
import { dirname } from "node:path";
import { mkdirSync } from "node:fs";
import * as sqliteVec from "sqlite-vec";
import { cacheDbPath } from "./config.js";
import type { EmbeddingModel, Template, TemplateInput } from "./types.js";
import { embeddingText } from "./embeddings.js";

export class TemplateDatabase {
  private db: Database.Database;
  private vecLoaded: boolean;

  constructor(dbPath = cacheDbPath()) {
    const dir = dirname(dbPath);
    mkdirSync(dir, { recursive: true });
    this.db = new Database(dbPath);
    this.db.pragma("journal_mode = WAL");
    this.vecLoaded = this.tryLoadSqliteVec();
    this.init();
  }

  private tryLoadSqliteVec(): boolean {
    try {
      sqliteVec.load(this.db);
      return true;
    } catch (err) {
      console.warn("sqlite-vec not available; semantic search disabled:", err);
      return false;
    }
  }

  private init() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        framework TEXT,
        title TEXT,
        description TEXT,
        github_url TEXT,
        owner TEXT,
        repository TEXT,
        use_cases TEXT,
        frameworks TEXT,
        css TEXT,
        databases TEXT,
        authentication TEXT,
        cms TEXT,
        experimentation TEXT,
        readme_text TEXT,
        install_command TEXT,
        detail_url TEXT,
        indexed_at INTEGER
      )
    `);
    this.db.exec(`
      CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(
        title, description, readme_text, tags
      )
    `);
    if (this.vecLoaded) {
      try {
        this.db.exec(`
          CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(embedding float[768])
        `);
      } catch (err) {
        console.warn("Failed to create embeddings virtual table:", err);
        this.vecLoaded = false;
      }
    }
  }

  reset() {
    this.db.exec("DROP TABLE IF EXISTS search");
    this.db.exec("DROP TABLE IF EXISTS embeddings");
    this.db.exec("DROP TABLE IF EXISTS templates");
    this.init();
  }

  isVecLoaded(): boolean {
    return this.vecLoaded;
  }

  async saveTemplates(
    templates: TemplateInput[],
    embeddingModel?: EmbeddingModel,
  ): Promise<void> {
    const insert = this.db.prepare<TemplateInput>(`
      INSERT OR REPLACE INTO templates
      (slug, framework, title, description, github_url, owner, repository,
       use_cases, frameworks, css, databases, authentication, cms, experimentation,
       readme_text, install_command, detail_url, indexed_at)
      VALUES
      (@slug, @framework, @title, @description, @github_url, @owner, @repository,
       @use_cases, @frameworks, @css, @databases, @authentication, @cms, @experimentation,
       @readme_text, @install_command, @detail_url, @indexed_at)
    `);
    const insertSearch = this.db.prepare<{
      rowid: number;
      title: string;
      description: string;
      readme_text: string;
      tags: string;
    }>(`
      INSERT OR REPLACE INTO search (rowid, title, description, readme_text, tags)
      VALUES (@rowid, @title, @description, @readme_text, @tags)
    `);
    const insertEmbedding = this.vecLoaded
      ? this.db.prepare<{ rowid: number; embedding: Buffer }>(`
          INSERT OR REPLACE INTO embeddings (rowid, embedding)
          VALUES (@rowid, @embedding)
        `)
      : null;

    const save = this.db.transaction((rows: TemplateInput[]) => {
      for (const t of rows) {
        const result = insert.run(t);
        const rowid = result.lastInsertRowid as number;
        const tags = [
          t.use_cases,
          t.frameworks,
          t.css,
          t.databases,
          t.authentication,
          t.cms,
        ]
          .filter(Boolean)
          .join(", ");
        insertSearch.run({
          rowid,
          title: t.title,
          description: t.description,
          readme_text: t.readme_text,
          tags,
        });
      }
    });

    if (!embeddingModel || !this.vecLoaded) {
      save(templates);
      return;
    }

    const texts = templates.map((t) => embeddingText(t));
    const vectors = await embeddingModel.encode(texts);

    const saveWithEmbeddings = this.db.transaction((rows: TemplateInput[]) => {
      for (let i = 0; i < rows.length; i++) {
        const t = rows[i];
        const result = insert.run(t);
        const rowid = result.lastInsertRowid as number;
        const tags = [
          t.use_cases,
          t.frameworks,
          t.css,
          t.databases,
          t.authentication,
          t.cms,
        ]
          .filter(Boolean)
          .join(", ");
        insertSearch.run({
          rowid,
          title: t.title,
          description: t.description,
          readme_text: t.readme_text,
          tags,
        });
        insertEmbedding!.run({
          rowid,
          embedding: Buffer.from(vectors[i].buffer),
        });
      }
    });

    saveWithEmbeddings(templates);
  }

  search(query: string, limit = 10): Template[] {
    return this.db
      .prepare(`
        SELECT t.* FROM templates t
        JOIN search s ON s.rowid = t.id
        WHERE search MATCH ?
        ORDER BY rank
        LIMIT ?
      `)
      .all(query, limit) as Template[];
  }

  semanticSearch(queryVector: Float32Array, limit = 10): Template[] {
    if (!this.vecLoaded) {
      throw new Error(
        "sqlite-vec extension not available. Semantic search requires sqlite-vec.",
      );
    }
    return this.db
      .prepare(`
        SELECT t.*, distance
        FROM embeddings e
        JOIN templates t ON t.id = e.rowid
        WHERE e.embedding MATCH ?
          AND k = ?
        ORDER BY distance
      `)
      .all(Buffer.from(queryVector.buffer), limit) as Template[];
  }

  get(slug: string): Template | undefined {
    // Slugs may be provided with or without a leading slash.
    const normalized = slug.startsWith("/") ? slug : `/${slug}`;
    return this.db
      .prepare("SELECT * FROM templates WHERE slug = ? OR slug = ?")
      .get(slug, normalized) as Template | undefined;
  }

  all(limit?: number): Template[] {
    let sql = "SELECT * FROM templates ORDER BY title";
    if (limit) {
      return this.db.prepare(`${sql} LIMIT ?`).all(limit) as Template[];
    }
    return this.db.prepare(sql).all() as Template[];
  }

  count(): number {
    const row = this.db.prepare("SELECT COUNT(*) as n FROM templates").get() as {
      n: number;
    };
    return row.n;
  }

  recentlyAdded(hours = 24, limit?: number): Template[] {
    const since = Math.floor(Date.now() / 1000) - hours * 3600;
    let sql = "SELECT * FROM templates WHERE indexed_at >= ? ORDER BY indexed_at DESC";
    if (limit) {
      return this.db.prepare(`${sql} LIMIT ?`).all(since, limit) as Template[];
    }
    return this.db.prepare(sql).all(since) as Template[];
  }

  trending(hours = 168, limit = 10, byCategory = false): { templates: Template[]; total: number; hours: number } | { grouped: Record<string, Template[]>; total: number; hours: number } {
    const recent = this.recentlyAdded(hours);
    if (!byCategory) {
      return { templates: recent.slice(0, limit), total: recent.length, hours };
    }
    const grouped: Record<string, Template[]> = {};
    for (const t of recent) {
      const category = t.frameworks || "uncategorized";
      for (const cat of category.split(",").map((c) => c.trim()).filter(Boolean)) {
        const key = cat || "uncategorized";
        grouped[key] = grouped[key] || [];
        grouped[key].push(t);
      }
    }
    for (const key of Object.keys(grouped)) {
      grouped[key] = grouped[key].slice(0, limit);
    }
    return { grouped, total: recent.length, hours };
  }

  recommend(
    stack: string[],
    { limit = 10, requireAllFrameworks = false }: { limit?: number; requireAllFrameworks?: boolean } = {},
  ): Array<Template & { recommend_score: number; recommend_matches: string[] }> {
    if (!stack.length) return [];
    const normalizedStack = stack.map((s) => s.trim().toLowerCase()).filter(Boolean);
    if (!normalizedStack.length) return [];

    const rows = this.all();
    const scored: Array<{ score: number; matches: Set<string>; template: Template }> = [];
    for (const t of rows) {
      const { score, matches } = this.scoreTemplate(t, normalizedStack);
      if (score <= 0) continue;
      if (requireAllFrameworks && !this.matchesAllFrameworks(t, normalizedStack)) continue;
      scored.push({ score, matches, template: t });
    }
    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, limit).map(({ score, matches, template }) => ({
      ...template,
      recommend_score: Math.round(score * 10000) / 10000,
      recommend_matches: Array.from(matches).sort(),
    }));
  }

  private scoreTemplate(t: Template, stack: string[]): { score: number; matches: Set<string> } {
    const matches = new Set<string>();
    const weights: Record<string, number> = {
      frameworks: 2.0,
      use_cases: 1.5,
      databases: 1.0,
      css: 0.8,
      authentication: 1.2,
      cms: 1.0,
      title: 1.0,
      description: 0.5,
    };
    let score = 0;
    for (const [field, weight] of Object.entries(weights)) {
      const value = String((t as unknown as Record<string, unknown>)[field] ?? "").toLowerCase();
      if (!value) continue;
      for (const term of stack) {
        if (value.includes(term)) {
          score += weight;
          matches.add(term);
        }
      }
    }
    return { score, matches };
  }

  private matchesAllFrameworks(t: Template, stack: string[]): boolean {
    const frameworks = (t.frameworks || "").toLowerCase();
    const frameworkTerms = stack.filter((term) => this.isFrameworkTerm(term));
    if (!frameworkTerms.length) return true;
    return frameworkTerms.every((term) => frameworks.includes(term));
  }

  private isFrameworkTerm(term: string): boolean {
    const frameworks = new Set([
      "next.js", "nuxt", "svelte", "astro", "hono", "express", "flask",
      "remix", "vue", "angular", "react", "solid", "qwik", "django",
      "fastapi", "rails", "laravel", "spring", "sveltekit", "gatsby",
    ]);
    return frameworks.has(term);
  }

  close() {
    this.db.close();
  }
}
