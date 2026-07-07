import he from "he";
import * as cheerio from "cheerio";
import type { AnyNode } from "domhandler";
import {
  BASE_URL,
  DEFAULT_CATEGORIES,
  FRAMEWORK_CATEGORIES,
  userAgent,
} from "./config.js";
import { TemplateDatabase } from "./db.js";
import type { DiscoveredTemplate, Template, TemplateInput } from "./types.js";

const { decode } = he;

import { embeddingText, getModel } from "./embeddings.js";
import type { EmbeddingModel } from "./types.js";

export interface ScraperOptions {
  delay?: number;
  maxWorkers?: number;
  dbPath?: string;
  embeddingModel?: EmbeddingModel | false;
}

export class VercelTemplateScraper {
  private delay: number;
  private maxWorkers: number;
  readonly db: TemplateDatabase;
  embeddingModel: EmbeddingModel | undefined;

  constructor(options: ScraperOptions = {}) {
    this.delay = options.delay ?? 0.5;
    this.maxWorkers = options.maxWorkers ?? 8;
    this.db = new TemplateDatabase(options.dbPath);
    this.embeddingModel =
      options.embeddingModel === false ? undefined : options.embeddingModel;
  }

  private async _get(url: string, retries = 3): Promise<string> {
    let lastErr: unknown;
    for (let attempt = 0; attempt < retries; attempt++) {
      try {
        const resp = await fetch(url, {
          headers: {
            "User-Agent": userAgent(),
            Accept:
              "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
          },
        });
        if (resp.status === 200) return await resp.text();
        if (resp.status === 429 || resp.status === 503) {
          await this.sleep(2 ** attempt * 1000);
          continue;
        }
        throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
      } catch (err) {
        lastErr = err;
        await this.sleep(1.5 ** attempt * 1000);
      }
    }
    throw lastErr ?? new Error(`Failed to fetch ${url}`);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async discoverTemplates(): Promise<Record<string, DiscoveredTemplate>> {
    const templates: Record<string, DiscoveredTemplate> = {};
    for (const category of DEFAULT_CATEGORIES) {
      const url = `${BASE_URL}/templates/${category}`;
      try {
        const html = await this._get(url);
        const regex =
          /data-template-card-wrapper[^>]*href="(\/templates\/[^"]+)".*?<h3[^>]*>([^<]+)<\/h3>.*?line-clamp-2[^>]*>([^<]+)/gs;
        let match: RegExpExecArray | null;
        while ((match = regex.exec(html)) !== null) {
          const slug = match[1].trim();
          if (!templates[slug]) {
            templates[slug] = {
              slug,
              framework: category,
              title: unescapeHtml(match[2].trim()),
              description: unescapeHtml(match[3].trim()),
              detail_url: `${BASE_URL}${slug}`,
            };
          }
        }
        await this.sleep(this.delay * 1000);
      } catch (err) {
        console.warn(`Warning: failed to discover ${category}: ${err}`);
      }
    }
    return templates;
  }

  async enrichTemplate(
    slug: string,
    category?: string,
  ): Promise<TemplateInput> {
    const url = `${BASE_URL}${slug}`;
    const html = await this._get(url);
    const $ = cheerio.load(html);

    const title = $("h1").first().text().trim() || "";
    const description =
      $("p")
        .filter((_: number, el: AnyNode) => {
          const cls = $(el).attr("class") || "";
          return cls.includes("text-sm") && cls.includes("text-gray-900");
        })
        .first()
        .text()
        .trim() || "";

    const scripts = $("script")
      .map((_: number, el: AnyNode) => $(el).text())
      .get()
      .join("\n");

    const githubUrl = extractJsonString(scripts, "githubUrl") || "";
    let owner = "";
    let repository = "";
    const m = githubUrl.match(/github\.com\/([^/]+)\/([^/]+)(?:\/tree\/.+)?/);
    if (m) {
      owner = m[1];
      repository = m[2];
    }

    const useCases = extractSidebarValues(scripts, "Use Cases").join(", ");
    const frameworks = extractSidebarValues(scripts, "Framework").join(", ");
    const css = extractSidebarValues(scripts, "CSS").join(", ");
    const databases = extractSidebarValues(scripts, "Database").join(", ");
    const auth = extractSidebarValues(scripts, "Authentication").join(", ");
    const cms = extractSidebarValues(scripts, "CMS").join(", ");
    const experimentation = extractSidebarValues(scripts, "Experimentation").join(
      ", ",
    );

    const readmeText = extractReadmeText(scripts) || "";
    const extractedInstall = extractInstallCommand(readmeText, scripts) || "";
    const data: TemplateInput = {
      slug,
      framework: frameworks || category || "",
      title,
      description,
      github_url: githubUrl,
      owner,
      repository,
      use_cases: useCases,
      frameworks,
      css,
      databases,
      authentication: auth,
      cms,
      experimentation,
      readme_text: readmeText,
      install_command: extractedInstall,
      detail_url: url,
      indexed_at: Math.floor(Date.now() / 1000),
    };
    if (category && FRAMEWORK_CATEGORIES.has(category) && !data.frameworks) {
      data.frameworks = category;
    }
    data.install_command = this.selectInstallCommand(data, extractedInstall);
    return data;
  }

  async index(concurrency?: number): Promise<number> {
    this.db.reset();
    const templates = await this.discoverTemplates();
    const slugs = Object.keys(templates);
    if (slugs.length === 0) return 0;

    const workers = concurrency ?? this.maxWorkers;
    const enriched: TemplateInput[] = [];

    const queue = [...slugs];
    let active = 0;

    await new Promise<void>((resolve, reject) => {
      const run = async () => {
        active++;
        while (queue.length > 0) {
          const slug = queue.shift()!;
          try {
            const category = templates[slug].framework;
            const data = await this.enrichTemplate(slug, category);
            if (!data.frameworks && category) {
              if (FRAMEWORK_CATEGORIES.has(category)) {
                data.frameworks = category;
              }
            }
            data.install_command = this.selectInstallCommand(
              data,
              data.install_command,
            );
            enriched.push(data);
          } catch (err) {
            console.warn(`Warning: failed to enrich ${slug}: ${err}`);
          }
        }
        active--;
        if (active === 0) {
          resolve();
        }
      };

      for (let i = 0; i < Math.min(workers, slugs.length); i++) {
        run().catch(reject);
      }
    });

    await this.db.saveTemplates(enriched, this.embeddingModel);
    return enriched.length;
  }

  private synthesizeInstallCommand(t: TemplateInput): string {
    const slug = t.slug || "";
    const github = t.github_url || "";
    const framework = (t.frameworks || t.framework || "").toLowerCase();

    const exampleMatch = github.match(
      /github\.com\/vercel\/vercel\/tree\/[^/]+\/examples\/([^/]+)$/,
    );
    if (exampleMatch && framework.includes("next")) {
      return `npx create-next-app --example ${exampleMatch[1]} my-app`;
    }
    if (github && framework.includes("next")) {
      const m = github.match(/\/examples\/([^/]+)$/);
      if (m) return `npx create-next-app --example ${m[1]} my-app`;
    }
    if (github) return `git clone ${github}`;
    const parts = slug.replace(/^\/+|\/+$/g, "").split("/");
    if (parts.length >= 2 && parts[0].toLowerCase().includes("next")) {
      return `npx create-next-app --example ${parts[parts.length - 1]} my-app`;
    }
    return "";
  }

  private isScaffoldOrClone(command: string): boolean {
    return (
      command.startsWith("npx create-") ||
      command.startsWith("npx create ") ||
      command.startsWith("npm create ") ||
      command.startsWith("yarn create ") ||
      command.startsWith("bunx create-") ||
      command.startsWith("bun create ") ||
      command.startsWith("git clone ")
    );
  }

  private isCreateNextApp(command: string): boolean {
    return /^(npx|npm|yarn|pnpm|bunx?)\s+(create-next-app|create\s+next-app)/.test(
      command,
    );
  }

  private selectInstallCommand(
    t: TemplateInput,
    extracted: string | undefined,
  ): string {
    const synthesized = this.synthesizeInstallCommand(t);
    const framework = (t.frameworks || t.framework || "").toLowerCase();
    if (
      synthesized &&
      this.isCreateNextApp(synthesized) &&
      (!extracted || !this.isCreateNextApp(extracted))
    ) {
      return synthesized;
    }
    if (extracted && this.isScaffoldOrClone(extracted)) return extracted;
    if (synthesized) return synthesized;
    return extracted || "";
  }

  search(query: string, limit = 10): Template[] {
    return this.db.search(query, limit);
  }

  async semanticSearch(query: string, limit = 10): Promise<Template[]> {
    if (!this.embeddingModel) {
      throw new Error(
        "No embedding model configured. Pass embeddingModel to the scraper or set up Ollama.",
      );
    }
    const vec = await this.embeddingModel.encodeSingle(query);
    return this.db.semanticSearch(vec, limit);
  }

  get(slug: string): Template | undefined {
    return this.db.get(slug);
  }

  stats(): { count: number } {
    return { count: this.db.count() };
  }

  recentlyAdded(hours = 24, limit?: number): Template[] {
    return this.db.recentlyAdded(hours, limit);
  }

  trending(hours = 168, limit = 10, byCategory = false): ReturnType<TemplateDatabase["trending"]> {
    return this.db.trending(hours, limit, byCategory);
  }

  close() {
    this.db.close();
  }
}

export function unescapeHtml(text: string): string {
  return decode(text);
}

export function unescapeJsonString(text: string): string {
  try {
    const escaped = text.replace(/"/g, '\\"');
    const parsed = JSON.parse(`"${escaped}"`);
    if (typeof parsed === "string") return decode(parsed);
  } catch {
    // fall through
  }
  return decode(text);
}

export function extractJsonString(text: string, key: string): string | null {
  const escaped = new RegExp(
    `\\\\"${regexEscape(key)}\\\\":\\s*\\\\"([^\\\\"]+)\\\\"`,
  );
  const m1 = escaped.exec(text);
  if (m1) return unescapeHtml(m1[1]);

  const plain = new RegExp(`"${regexEscape(key)}":\\s*"([^"]+)"`);
  const m2 = plain.exec(text);
  return m2 ? m2[1] : null;
}

export function extractSidebarValues(text: string, label: string): string[] {
  const values: string[] = [];
  const pattern = new RegExp(
    `\\\\"children\\\\":\\\\"${regexEscape(label)}\\\\"`,
    "g",
  );
  let match: RegExpExecArray | null;
  while ((match = pattern.exec(text)) !== null) {
    const window = text.slice(
      match.index + match[0].length,
      match.index + match[0].length + 900,
    );
    const vals = window.match(/\\"children\\":\\"([^\\"]{1,60})\\"/g) || [];
    for (const v of vals) {
      const inner = v.match(/\\"children\\":\\"([^\\"]+)\\"/)?.[1] ?? v;
      const decoded = unescapeHtml(inner);
      if (
        decoded === label ||
        ["GitHub", "Owner", "Repository", "Deploy", "Stack"].includes(decoded) ||
        decoded.startsWith("$") ||
        decoded === "Related Templates" ||
        decoded.length < 2
      ) {
        continue;
      }
      values.push(decoded);
      if (values.length >= 6) break;
    }
    if (values.length >= 6) break;
  }
  return values;
}

export function extractReadmeText(text: string): string | null {
  const refMatch = /\\"readmeText\\":\\"\$(\w+)\\"/.exec(text);
  if (refMatch) {
    const raw = extractFlightChunk(text, refMatch[1]);
    if (raw) return unescapeJsonString(raw);
  }

  const m1 = /\\"readmeText\\":\\"([^\\"]{200,})\\"/.exec(text);
  if (m1) return unescapeJsonString(m1[1]);

  const m2 = /"readmeText":"([^"]{200,})"/.exec(text);
  if (m2) return unescapeJsonString(m2[1]);

  const m3 = /(\\n#[^\\"]{200,})/.exec(text);
  if (m3) return unescapeJsonString(m3[1].replace(/\\n/g, "\n"));

  return null;
}

export function extractFlightChunk(text: string, refId: string): string | null {
  const marker = `${refId}:`;
  const idx = text.indexOf(marker);
  if (idx === -1) return null;
  const pushMarker = 'self.__next_f.push([1,"';
  const pushIdx = text.indexOf(pushMarker, idx);
  if (pushIdx === -1) return null;
  const start = pushIdx + pushMarker.length;
  let i = start;
  while (i < text.length) {
    if (text[i] === "\\" && i + 1 < text.length && text[i + 1] === '"') {
      i += 2;
    } else if (
      text[i] === '"' &&
      i + 2 < text.length &&
      text.slice(i + 1, i + 3) === "])"
    ) {
      return text.slice(start, i);
    } else {
      i++;
    }
  }
  return null;
}

export function extractInstallCommand(
  readmeText: string,
  scripts: string,
): string | null {
  const scaffoldPrefixes = [
    "npx create-",
    "npx create ",
    "npm create ",
    "yarn create ",
    "bunx create-",
    "bun create ",
    "git clone ",
  ];

  for (const block of readmeText.matchAll(
    /```(?:bash|sh|shell)?\n?(.*?)```/gs,
  )) {
    for (const line of block[1].split("\n")) {
      const trimmed = line.trim();
      if (scaffoldPrefixes.some((p) => trimmed.startsWith(p))) return trimmed;
    }
  }

  for (const block of readmeText.matchAll(
    /```(?:bash|sh|shell)?\n?(.*?)```/gs,
  )) {
    for (const line of block[1].split("\n")) {
      const trimmed = line.trim();
      if (
        trimmed.startsWith("npx ") ||
        trimmed.startsWith("npm ") ||
        trimmed.startsWith("yarn ") ||
        trimmed.startsWith("pnpm ") ||
        trimmed.startsWith("bun ") ||
        trimmed.startsWith("bunx ")
      ) {
        return trimmed;
      }
    }
  }

  const patterns = [
    /(?:\\")?npx\s+create-[\-\w]+(?:\s+[\-\w./=]+)*(?:\\")?/,
    /(?:\\")?git clone\s+\S+(?:\\")?/,
    /(?:\\")?npx\s+[\-\w]+(?:\s+[\-\w./=]+)*(?:\\")?/,
  ];
  for (const pattern of patterns) {
    const m = pattern.exec(scripts);
    if (m) return unescapeHtml(m[0].trim().replace(/^"|"$/g, ""));
  }

  return null;
}

function regexEscape(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
