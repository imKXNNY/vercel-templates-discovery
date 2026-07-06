# Vercel Templates Discovery

> Agentic CLI for discovering, indexing, and searching [Vercel Templates](https://vercel.com/templates). No public API exists — this tool fills the gap for agents and developers who want a searchable, local catalog with install commands.

## Quick start (Python)

```bash
# Install from PyPI (once published)
pip install vercel-templates-discovery

# Or install locally for development
pip install -e ".[dev]"

# Or run via Docker
docker run --rm ghcr.io/imkxnnny/vercel-templates-discovery:latest vercel-templates --help

# Index the catalog
vercel-templates index

# 3. Search
vercel-templates search "AI chatbot"
vercel-templates search "ecommerce" --limit 3
vercel-templates search "AI chatbot" --semantic  # semantic search by intent

# 4. Semantic search
vercel-templates semantic "AI chatbot"
vercel-templates semantic "ecommerce" --limit 3

# 5. Show details
vercel-templates show /templates/next.js/chatbot

# 6. Export to JSON
vercel-templates export --output templates.json
```

## Quick start (TypeScript / WSL)

```bash
# Install globally from npm (published)
npm install -g @imkxnny/vercel-templates-discovery

# Or work locally
cd ts
npm install

# Build once, or run via tsx
npm run build
npm run typecheck:all
npm test

# Index the catalog
npx tsx src/cli.ts index

# Search / show
npx tsx src/cli.ts search "AI chatbot" --json
npx tsx src/cli.ts show /templates/next.js/chatbot --json
```

## Why this exists

Vercel maintains a curated library of high-quality templates, but provides no SDK, CLI, or API for discovering them. This tool:

- Crawls the Vercel Templates gallery (~277 templates).
- Extracts metadata, GitHub URLs, and install commands.
- Stores everything in a local SQLite cache with full-text search.
- Exposes a simple CLI that agents can call or shell out to.

## Architecture

```text
vercel_templates/          # Python implementation
├── config.py              # categories, cache path, constants
├── scraper.py             # crawler + detail extractor + SQLite cache
└── cli.py                 # Typer CLI

ts/                        # TypeScript / Node implementation
├── src/
│   ├── scraper.ts         # crawler + detail extractor
│   ├── db.ts              # SQLite cache + FTS5 search
│   ├── cli.ts             # Commander CLI
│   ├── mcp-server.ts      # stdio JSON-RPC MCP server
│   └── index.ts           # library exports
├── tests/
│   └── scraper.test.ts    # vitest tests
└── package.json
```

The scraper uses `fetch` + `cheerio` + regex to parse Vercel's server-rendered pages and Next.js flight payloads. Because the catalog is small, the entire index can be rebuilt in under a minute.

## Commands

| Command | Description |
|---------|-------------|
| `index` | Crawl and index the full catalog |
| `search QUERY` | Full-text search over titles, descriptions, tags |
| `search QUERY --semantic` | Semantic search over embeddings (requires `semantic` extra) |
| `semantic QUERY` | Shorthand for semantic search |
| `show SLUG` | Show full details for a template |
| `export` | Dump the indexed catalog to JSON |
| `stats` | Show framework/category counts |
| `serve` | Start the REST API server |

## Semantic search

Semantic search is opt-in and requires the `semantic` extra:

```bash
pip install -e ".[semantic]"
```

It uses `sqlite-vec` for on-disk vector search and an embedding model from Ollama (default: `nomic-embed-text:latest`). The embedding model URL and name can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `VTD_OLLAMA_URL` | `http://localhost:11434/api/embed` | Ollama embeddings endpoint |
| `VTD_EMBEDDING_MODEL` | `nomic-embed-text:latest` | Model name passed to Ollama |

To build an index with embeddings, run:

```bash
vercel-templates index   # automatically generates embeddings when semantic extra is installed
```

Then query:

```bash
vercel-templates semantic "AI chatbot" --limit 5
vercel-templates search "AI chatbot" --semantic
```

Without Ollama, the fallback is a deterministic fake model that produces sparse token-frequency vectors. It is useful for CI but not for quality results.

## REST API server

Run the server with:

```bash
vercel-templates serve
# or
vercel-templates serve --host 0.0.0.0 --port 8080
```

Endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /templates?q=...&limit=...` | Search or list templates |
| `GET /templates/semantic?q=...&limit=...` | Semantic search (requires `semantic` extra) |
| `GET /templates/{slug}` | Get one template by slug (e.g. `/templates/next.js/chatbot`) |
| `GET /categories` | List frameworks and use cases |

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
- `search_templates_semantic(query, limit)` — semantic search over embeddings
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

### Hermes skill

A Hermes skill wrapper is provided under `skills/vercel-templates/`. Copy or symlink the skill into your Hermes profile's `skills/` directory:

```bash
# Windows native Hermes example
copy /Y skills\vercel-templates %LOCALAPPDATA%\hermes\skills\vercel-templates
# or Hermes profile path: ~/.hermes/profiles/default/skills/vercel-templates
```

The skill exposes the same tools as the MCP server (including `search_templates_semantic`) and can be used directly by Hermes agents.

## Project status

See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for the roadmap, milestones, and backlog.

## License

MIT
