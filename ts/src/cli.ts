import { Command } from "commander";
import { VercelTemplateScraper } from "./scraper.js";

const program = new Command();

program
  .name("vercel-templates")
  .description("Agentic discovery for Vercel Templates")
  .version("0.2.0");

program
  .command("index")
  .description("Re-index the full Vercel Templates catalog")
  .option("-c, --concurrency <n>", "number of concurrent detail fetches", "8")
  .option("-d, --db <path>", "path to the SQLite cache file")
  .action(async (options) => {
    const scraper = new VercelTemplateScraper({ dbPath: options.db });
    try {
      const count = await scraper.index(Number(options.concurrency));
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
  .action(async (query, options) => {
    const scraper = new VercelTemplateScraper({ dbPath: options.db });
    try {
      const rows = scraper.search(query, Number(options.limit));
      if (options.json) {
        console.log(JSON.stringify(rows, null, 2));
      } else {
        for (const t of rows) {
          console.log(`${t.title} — ${t.slug}`);
          console.log(`  ${t.description.slice(0, 120)}...`);
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
