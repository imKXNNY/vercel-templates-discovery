# Vercel Templates Discovery

> Agentic CLI for discovering, indexing, and searching [Vercel Templates](https://vercel.com/templates). No public API exists — this tool fills the gap for agents and developers who want a searchable, local catalog with install commands.

## Quick start

```bash
# Install globally from npm
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
# or from the built dist
npx vercel-templates index

# Search / show
npx vercel-templates search "AI chatbot" --json
npx vercel-templates show /templates/next.js/chatbot --json
```

## Why this exists

Vercel maintains a curated library of high-quality templates, but provides no SDK, CLI, or API for discovering them. This tool:

- Crawls the Vercel Templates gallery.
- Extracts metadata, GitHub URLs, and install commands.
- Stores everything in a local SQLite cache with full-text search.
- Exposes a simple CLI that agents can call or shell out to.

## Architecture

```text
ts/src/
├── scraper.ts         # crawler + detail extractor
├── db.ts              # SQLite cache + FTS5 search
├── cli.ts             # Commander CLI
├── mcp-server.ts      # stdio JSON-RPC MCP server
└── index.ts           # library exports
```

The scraper uses `fetch` + `cheerio` + regex to parse Vercel's server-rendered pages and Next.js flight payloads.

## Commands

| Command | Description |
|---------|-------------|
| `index` | Crawl and index the full catalog |
| `search QUERY` | Full-text search over titles, descriptions, tags |
| `search QUERY --semantic` | Semantic search over embeddings (requires Ollama) |
| `semantic QUERY` | Shorthand for semantic search |
| `show SLUG` | Show full details for a template |
| `stats` | Show framework/category counts |
| `serve` | Start the REST API server |

## Semantic search

Semantic search requires a local Ollama instance with an embedding model (default: `nomic-embed-text-v2-moe:latest`). The embedding model URL and name can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `VTD_OLLAMA_URL` | `http://localhost:11434/api/embed` | Ollama embeddings endpoint |
| `VTD_EMBEDDING_MODEL` | `nomic-embed-text-v2-moe:latest` | Model name passed to Ollama |

> **Note:** When you switch embedding models, vectors in the existing index are no longer semantically compatible. Run `vercel-templates index --reset` and re-index.

```bash
vercel-templates index
vercel-templates semantic "AI chatbot" --limit 5
vercel-templates search "AI chatbot" --semantic
```

## REST API server

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
| `GET /templates/semantic?q=...&limit=...` | Semantic search |
| `GET /templates/{slug}` | Get one template by slug |
| `GET /categories` | List frameworks and use cases |

## Agentic usage

### MCP server

```bash
vercel-templates-mcp
```

Available tools:
- `search_templates(query, limit)`
- `search_templates_semantic(query, limit)`
- `get_template(slug)`
- `list_categories()`

Example MCP client config (Claude Desktop / Cursor):

```json
{
  "mcpServers": {
    "vercel-templates": {
      "command": "npx",
      "args": ["@imkxnny/vercel-templates-discovery-mcp"]
    }
  }
}
```

## Python implementation

A Python implementation is also available on PyPI as `vercel-templates-discovery`. See the [GitHub repository](https://github.com/imKXNNY/vercel-templates-discovery) for details.

## License

MIT
