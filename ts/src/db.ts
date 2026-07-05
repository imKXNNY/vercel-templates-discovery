import Database from "better-sqlite3";
import { dirname } from "node:path";
import { mkdirSync } from "node:fs";
import { cacheDbPath } from "./config.js";
import type { Template, TemplateInput } from "./types.js";

export class TemplateDatabase {
  private db: Database.Database;

  constructor(dbPath = cacheDbPath()) {
    const dir = dirname(dbPath);
    mkdirSync(dir, { recursive: true });
    this.db = new Database(dbPath);
    this.db.pragma("journal_mode = WAL");
    this.init();
  }

  init() {
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
  }

  reset() {
    this.db.exec("DROP TABLE IF EXISTS search");
    this.db.exec("DROP TABLE IF EXISTS templates");
    this.init();
  }

  saveTemplates(templates: TemplateInput[]) {
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

    save(templates);
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

  get(slug: string): Template | undefined {
    return this.db
      .prepare("SELECT * FROM templates WHERE slug = ?")
      .get(slug) as Template | undefined;
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

  close() {
    this.db.close();
  }
}