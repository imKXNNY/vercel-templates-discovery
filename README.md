# Vercel Templates Discovery

An agentic CLI for discovering, indexing, and searching Vercel Templates.

## Why

Vercel's curated template gallery (https://vercel.com/templates) has no public API or CLI for discovery. This tool crawls the gallery, indexes ~267 templates, and exposes a searchable local cache with metadata including GitHub URLs and install commands.

## Install

```bash
cd /c/Users/kenny/Projects/vercel-templates-discovery
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
# Index the catalog (crawls category pages + detail pages)
vercel-templates index

# Search the index
vercel-templates search "AI chatbot"
vercel-templates search "Next.js ecommerce" --limit 5

# Show details for a specific template
vercel-templates show /templates/next.js/chatbot

# Export the index to JSON
vercel-templates export --output templates.json
```

## How it works

- **Category crawl**: visits each Vercel template category page and extracts template slugs, titles, and descriptions from the SSR'd HTML.
- **Detail crawl**: visits each template's detail page and extracts GitHub URL, use-case/framework tags, README, and install commands.
- **SQLite cache**: stores everything in `~/.vercel_templates/templates.db`.
- **Search**: keyword search over title, description, tags, and README; optionally ranks by relevance.

## Data freshness

The catalog is small (~267 templates). Running `index` refreshes the entire cache. By default it respects Vercel's servers with modest concurrency and retries.

## License

MIT
