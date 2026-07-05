import { VercelTemplateScraper } from "../src/scraper.js";

async function main() {
  const s = new VercelTemplateScraper();
  const slug = process.argv[2] || "/templates/next.js/nextjs-boilerplate";
  try {
    const data = await s.enrichTemplate(slug);
    console.log(JSON.stringify(data, null, 2));
  } finally {
    s.close();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
