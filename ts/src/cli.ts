import { Command } from "commander";
import { VercelTemplateScraper } from "./scraper.js";
import { getModel } from "./embeddings.js";

const program = new Command();

program
  .name("vercel-templates")
  .description("Agentic discovery for Vercel Templates")
  .version("0.2.3");

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

program.parse();
