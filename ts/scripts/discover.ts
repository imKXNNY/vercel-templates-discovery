import { VercelTemplateScraper } from "../src/scraper.js";

async function main() {
  const s = new VercelTemplateScraper();
  const discovered = await s.discoverTemplates();
  console.log(`Discovered: ${Object.keys(discovered).length}`);
  console.log(Object.values(discovered).slice(0, 3));
  s.close();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
