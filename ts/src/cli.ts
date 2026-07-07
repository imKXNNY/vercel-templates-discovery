import { Command } from "commander";
import { VercelTemplateScraper } from "./scraper.js";
import { getModel } from "./embeddings.js";

const program = new Command();

program
  .name("vercel-templates")
  .description("Agentic discovery for Vercel Templates")
  .version("1.0.0");

function parseConcurrency(raw: string | undefined): number {
  const n = raw === undefined ? 8 : Number(raw);
  if (!Number.isFinite(n) || n < 1 || n > 64) {
    console.error(`Invalid concurrency: ${raw}. Using default 8.`);
    return 8;
  }
  return Math.floor(n);
}

program
  .command("index")
  .description("Re-index the full Vercel Templates catalog")
  .option("-c, --concurrency <n>", "number of concurrent detail fetches", "8")
  .option("-d, --db <path>", "path to the SQLite cache file")
  .option("--reset", "drop existing index before re-indexing")
  .action(async (options) => {
    const scraper = new VercelTemplateScraper({ dbPath: options.db });
    try {
      if (options.reset) {
        scraper.db.reset();
        console.log("Existing index dropped.");
      }
      const count = await scraper.index(parseConcurrency(options.concurrency));
      console.log(`Indexed ${count} templates`);
    } finally {
      scraper.close();
    }
  });

program
  .command("search <query>")
  .description("Search indexed templates")
  .option("-l, --limit <n>", "max results", "10")
  .option("-j, --json", "output as JSON")
  .option("-d, --db <path>", "path to the SQLite cache file")
  .option("--semantic", "use semantic search (requires Ollama)")
  .action(async (query, options) => {
    const scraper = new VercelTemplateScraper({ dbPath: options.db });
    try {
      let rows: unknown[];
      if (options.semantic) {
        const model = await getModel();
        scraper.embeddingModel = model;
        rows = await scraper.semanticSearch(query, Number(options.limit));
      } else {
        rows = scraper.search(query, Number(options.limit));
      }
      if (options.json) {
        console.log(JSON.stringify(rows, null, 2));
      } else {
        for (const t of rows as Array<{ title: string; slug: string; description: string; distance?: number }>) {
          let line = `${t.title} — ${t.slug}`;
          if (typeof t.distance === "number") {
            line += ` (distance: ${t.distance.toFixed(4)})`;
          }
          console.log(line);
          const snippet = t.description.slice(0, 120);
          const ellipsis = t.description.length > 120 ? "..." : "";
          console.log(`  ${snippet}${ellipsis}`);
        }
      }
    } finally {
      scraper.close();
    }
  });

program
  .command("semantic <query>")
  .description("Semantic search over indexed templates (requires Ollama)")
  .option("-l, --limit <n>", "max results", "10")
  .option("-j, --json", "output as JSON")
  .option("-d, --db <path>", "path to the SQLite cache file")
  .action(async (query, options) => {
    const scraper = new VercelTemplateScraper({ dbPath: options.db });
    try {
      const model = await getModel();
      scraper.embeddingModel = model;
      const rows = await scraper.semanticSearch(query, Number(options.limit));
      if (options.json) {
        console.log(JSON.stringify(rows, null, 2));
      } else {
        for (const t of rows as Array<{ title: string; slug: string; description: string; distance?: number }>) {
          console.log(`${t.title} — ${t.slug} (distance: ${(t.distance ?? 0).toFixed(4)})`);
          const snippet = t.description.slice(0, 120);
          const ellipsis = t.description.length > 120 ? "..." : "";
          console.log(`  ${snippet}${ellipsis}`);
        }
      }
    } finally {
      scraper.close();
    }
  });

program
  .command("show <slug>")
  .description("Show details for a specific template")
  .option("-j, --json", "output as JSON")
  .option("-d, --db <path>", "path to the SQLite cache file")
  .action(async (slug, options) => {
    const scraper = new VercelTemplateScraper({ dbPath: options.db });
    try {
      const t = scraper.get(slug);
      if (!t) {
        console.error(`Template not found: ${slug}`);
        process.exit(1);
      }
      if (options.json) {
        console.log(JSON.stringify(t, null, 2));
      } else {
        console.log(`Title: ${t.title}`);
        console.log(`Description: ${t.description}`);
        console.log(`GitHub: ${t.github_url}`);
        console.log(`Install: ${t.install_command}`);
      }
    } finally {
      scraper.close();
    }
  });

program
  .command("diff <slug-a> <slug-b>")
  .description("Compare two indexed templates side by side")
  .option("-j, --json", "output as JSON")
  .option(
    "-f, --fields <fields>",
    "comma-separated fields to compare",
    "title,description,frameworks,use_cases,github_url,install_command,readme_text",
  )
  .option("-d, --db <path>", "path to the SQLite cache file")
  .action(async (slugA: string, slugB: string, options) => {
    const scraper = new VercelTemplateScraper({ dbPath: options.db });
    try {
      const a = scraper.get(slugA);
      const b = scraper.get(slugB);
      if (!a || !b) {
        const missing = a ? slugB : slugA;
        console.error(`Template not found: ${missing}`);
        process.exit(1);
      }
      const fields = options.fields
        .split(",")
        .map((f: string) => f.trim())
        .filter(Boolean);
      const comparison: Record<string, { a: unknown; b: unknown; same: boolean }> = {};
      for (const field of fields) {
        const aVal = (a as unknown as Record<string, unknown>)[field] ?? "";
        const bVal = (b as unknown as Record<string, unknown>)[field] ?? "";
        comparison[field] = { a: aVal, b: bVal, same: aVal === bVal };
      }
      if (options.json) {
        console.log(JSON.stringify(comparison, null, 2));
      } else {
        console.log(`Diff: ${slugA} vs ${slugB}`);
        for (const [field, values] of Object.entries(comparison)) {
          const marker = values.same ? "=" : "≠";
          console.log(`${marker} ${field}`);
          console.log(`  A: ${String(values.a).slice(0, 120)}`);
          console.log(`  B: ${String(values.b).slice(0, 120)}`);
        }
      }
    } finally {
      scraper.close();
    }
  });

program
  .command("stats")
  .description("Show catalog statistics")
  .option("-d, --db <path>", "path to the SQLite cache file")
  .action(async (options) => {
    const scraper = new VercelTemplateScraper({ dbPath: options.db });
    try {
      const stats = scraper.stats();
      console.log(`Indexed templates: ${stats.count}`);
    } finally {
      scraper.close();
    }
  });

program
  .command("recent")
  .description("Show templates added to the index recently")
  .option("-h, --hours <n>", "how many hours back to look", "24")
  .option("-l, --limit <n>", "max results", "10")
  .option("-j, --json", "output as JSON")
  .option("-d, --db <path>", "path to the SQLite cache file")
  .action(async (options) => {
    const scraper = new VercelTemplateScraper({ dbPath: options.db });
    try {
      const rows = scraper.recentlyAdded(Number(options.hours), Number(options.limit));
      if (options.json) {
        console.log(JSON.stringify(rows, null, 2));
      } else {
        console.log(`Templates indexed in the last ${options.hours} hours:`);
        for (const t of rows as Array<{ title: string; slug: string; frameworks: string; indexed_at: number }>) {
          const dt = new Date(t.indexed_at * 1000).toISOString().slice(0, 16).replace("T", " ");
          console.log(`${t.title} — ${t.slug} (${t.frameworks}) at ${dt}`);
        }
      }
    } finally {
      scraper.close();
    }
  });

program
  .command("trending")
  .description("Show trending (recently added) templates")
  .option("-h, --hours <n>", "how many hours back to look", "168")
  .option("-l, --limit <n>", "max results per category", "10")
  .option("--by-category", "group results by category")
  .option("-j, --json", "output as JSON")
  .option("-d, --db <path>", "path to the SQLite cache file")
  .action(async (options) => {
    const scraper = new VercelTemplateScraper({ dbPath: options.db });
    try {
      const data = scraper.trending(Number(options.hours), Number(options.limit), options.byCategory);
      if (options.json) {
        console.log(JSON.stringify(data, null, 2));
      } else {
        if ("grouped" in data) {
          for (const [category, items] of Object.entries(data.grouped)) {
            console.log(`Trending in ${category}:`);
            for (const t of items as Array<{ title: string; slug: string; indexed_at: number }>) {
              const dt = new Date(t.indexed_at * 1000).toISOString().slice(0, 16).replace("T", " ");
              console.log(`  ${t.title} — ${t.slug} at ${dt}`);
            }
          }
        } else {
          console.log(`Trending templates in the last ${options.hours} hours (${data.total} total):`);
          for (const t of data.templates as Array<{ title: string; slug: string; frameworks: string; indexed_at: number }>) {
            const dt = new Date(t.indexed_at * 1000).toISOString().slice(0, 16).replace("T", " ");
            console.log(`${t.title} — ${t.slug} (${t.frameworks}) at ${dt}`);
          }
        }
      }
    } finally {
      scraper.close();
    }
  });

program
  .command("recommend <stack>")
  .description("Recommend templates based on a target stack or feature set")
  .option("-l, --limit <n>", "max results", "10")
  .option("--require-all-frameworks", "require all framework terms to match")
  .option("-j, --json", "output as JSON")
  .option("-d, --db <path>", "path to the SQLite cache file")
  .action(async (stack: string, options) => {
    const scraper = new VercelTemplateScraper({ dbPath: options.db });
    try {
      const stackList = stack.split(",").map((s) => s.trim()).filter(Boolean);
      if (!stackList.length) {
        console.error("Provide at least one stack term.");
        process.exit(1);
      }
      const rows = scraper.recommend(stackList, {
        limit: Number(options.limit),
        requireAllFrameworks: options.requireAllFrameworks,
      });
      if (options.json) {
        console.log(JSON.stringify(rows, null, 2));
      } else {
        console.log(`Recommended templates for: ${stack}`);
        for (const t of rows as Array<{ title: string; slug: string; frameworks: string; recommend_score: number; recommend_matches: string[] }>) {
          console.log(
            `${t.title} — ${t.slug} (${t.frameworks}) score: ${t.recommend_score.toFixed(4)} matches: ${t.recommend_matches.join(", ")}`,
          );
        }
      }
    } finally {
      scraper.close();
    }
  });

program.parse();
