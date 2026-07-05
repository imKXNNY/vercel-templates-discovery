# Vercel Templates Discovery

> Agentic CLI for discovering, indexing, and searching [Vercel Templates](https://vercel.com/templates). No public API exists — this tool fills the gap for agents and developers who want a searchable, local catalog with install commands.

## Quick start

```bash
# 1. Install
pip install -e ".[dev]"

# 2. Index the catalog
vercel-templates index

# 3. Search
vercel-templates search "AI chatbot"
vercel-templates search "ecommerce" --limit 3

# 4. Show details
vercel-templates show /templates/next.js/chatbot

# 5. Export to JSON
vercel-templates export --output templates.json
```

## Why this exists

Vercel maintains a curated library of high-quality templates, but provides no SDK, CLI, or API for discovering them. This tool:

- Crawls the Vercel Templates gallery (~277 templates).
- Extracts metadata, GitHub URLs, and install commands.
- Stores everything in a local SQLite cache with full-text search.
- Exposes a simple CLI that agents can call or shell out to.

## Architecture

```text
vercel_templates/
├── config.py      # categories, cache path, constants
├── scraper.py     # crawler + detail extractor + SQLite cache
└── cli.py         # Typer CLI
```

The scraper uses `requests` + `BeautifulSoup` + regex to parse Vercel's server-rendered pages and Next.js flight payloads. Because the catalog is small, the entire index can be rebuilt in ~60 seconds.

## Commands

| Command | Description |
|---------|-------------|
| `index` | Crawl and index the full catalog |
| `search QUERY` | Full-text search over titles, descriptions, tags |
| `show SLUG` | Show full details for a template |
| `export` | Dump the indexed catalog to JSON |
| `stats` | Show framework/category counts |

## Agentic usage

The CLI is designed to be easy for agents to consume:

```bash
# JSON output for downstream parsing
vercel-templates search "AI chatbot" --json
vercel-templates show /templates/next.js/chatbot --json
```

### MCP server

An MCP (Model Context Protocol) server is included for direct agent integration:

```bash
# Start the MCP server
python -m vercel_templates.mcp_server
# or
vercel-templates-mcp
```

Available tools:
- `search_templates(query, limit)` — search the catalog
- `get_template(slug)` — get full details for a template
- `list_categories()` — list available categories/frameworks

Example MCP client config (Claude Desktop / Cursor):

```json
{
  "mcpServers": {
    "vercel-templates": {
      "command": "python",
      "args": ["-m", "vercel_templates.mcp_server"]
    }
  }
}
```

## Project status

See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for the roadmap, milestones, and backlog.

## License

MIT
