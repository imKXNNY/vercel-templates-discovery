---
name: vercel-templates-discovery
description: Discover, search, compare, and recommend Vercel Templates. Use when the user asks "find a Vercel template for X", "compare Vercel templates", "recommend a starter for Y", or needs to bootstrap a project from the Vercel Templates gallery.
version: "1.0.0"
author: imKXNNY
license: MIT
metadata:
  compatibility:
    - hermes
    - claude-code
    - cursor
    - copilot
    - codex
    - openai-agents
  tags:
    - vercel
    - templates
    - discovery
    - scaffolding
    - agentic
  related_skills:
    - mcp
    - github
---

# Vercel Templates Discovery

This skill helps agents find, compare, and recommend the right [Vercel Template](https://vercel.com/templates) for a user's project. It drives the local `vercel-templates` CLI, the included REST API, and the MCP server. No public Vercel API is used; the tool scrapes and caches the gallery locally into a searchable SQLite database.

## When to use

- The user wants to find a Vercel Template for a specific framework, use case, or stack.
- The user asks "what templates exist for X?", "find me a starter for Y", or "compare Vercel templates".
- You need to bootstrap a project from a Vercel Template and need the install command or GitHub URL.
- The user wants to keep the local template index up to date.

## Do not use

- When the user is writing a new template from scratch (this skill only searches the existing gallery).
- When the user is asking about Vercel deployment, configuration, or billing unrelated to templates.
- As a replacement for the official Vercel Templates website when the user wants to browse visually.

## Installation

Pick the runtime the user already has installed:

```bash
# Python (CLI + REST server + MCP server)
pip install "vercel-templates-discovery[server,semantic]"

# Node / npm
npm install -g @imkxnny/vercel-templates-discovery

# Docker (local build; published image is built on tags)
docker build -t vercel-templates-discovery .
```

Semantic search requires a running Ollama instance (default: `http://localhost:11434`). If Ollama is unavailable, the Python tool errors out; the npm package falls back to a fake embedding model and logs a warning.

## Indexing

Always make sure the catalog is indexed before searching or comparing. The first index takes under a minute.

```bash
vercel-templates index
```

Reset and rebuild from scratch:

```bash
vercel-templates index --reset
```

Verify the index exists:

```bash
vercel-templates stats
```

## Search

### Keyword search

```bash
vercel-templates search "AI chatbot" --limit 10
vercel-templates search "ecommerce" --json
```

### Semantic search (requires Ollama)

```bash
vercel-templates search "AI chatbot" --semantic --limit 10
vercel-templates semantic "authentication dashboard" --limit 5
```

### Show details

```bash
vercel-templates show /templates/next.js/chatbot
vercel-templates show /templates/next.js/chatbot --json
```

Slugs may be provided with or without the leading `/`.

### Compare two templates

```bash
vercel-templates diff /templates/next.js/chatbot /templates/astro/chatbot
vercel-templates diff /templates/next.js/chatbot /templates/astro/chatbot --json
```

### Recommend by stack

```bash
vercel-templates recommend "next.js, ai, tailwind" --limit 5
```

### Export the catalog

```bash
vercel-templates export --output templates.json
vercel-templates export --output templates.json --include-readmes
```

## REST API

Start the API server:

```bash
vercel-templates serve --host 0.0.0.0 --port 8080
```

Useful endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /templates?q=...&limit=...` | Keyword search |
| `GET /templates/semantic?q=...&limit=...` | Semantic search |
| `GET /templates/recommend?stack=...` | Recommend by stack |
| `GET /templates/{slug}` | Get one template by slug |
| `GET /categories` | List frameworks and use cases |

## MCP server

Start the stdio MCP server (blocks and speaks JSON-RPC on stdin/stdout):

```bash
vercel-templates-mcp
```

or

```bash
python -m vercel_templates.mcp_server
```

Available tools:

- `search_templates(query, limit)` — keyword search
- `search_templates_semantic(query, limit)` — semantic search
- `get_template(slug)` — get details by slug
- `list_categories()` — list frameworks and use cases
- `recommend_templates(stack, limit)` — recommend by stack/features
- `list_recent_templates()` — recently added templates
- `list_trending_templates()` — trending templates

### Claude Desktop / Cursor configuration

```json
{
  "mcpServers": {
    "vercel-templates": {
      "command": "vercel-templates-mcp"
    }
  }
}
```

### Hermes installation

Copy or symlink this skill into the Hermes profile's `skills/` directory:

```bash
# Windows native Hermes
copy /Y skills\productivity\vercel-templates-discovery %LOCALAPPDATA%\hermes\skills\vercel-templates-discovery

# WSL / Linux / macOS
ln -s skills/productivity/vercel-templates-discovery ~/.hermes/profiles/default/skills/vercel-templates-discovery
```

## Environment variables

| Variable | Default | Effect |
|----------|---------|--------|
| `VTD_DB_PATH` | `<module_dir>/templates.db` | SQLite cache location |
| `VTD_OLLAMA_URL` | `http://localhost:11434/api/embed` | Ollama embeddings endpoint |
| `VTD_EMBEDDING_MODEL` | `nomic-embed-text-v2-moe:latest` | Embedding model name |

## Output format

Keyword search returns a JSON array of templates:

```json
[
  {
    "slug": "/templates/next.js/chatbot",
    "title": "Chatbot",
    "description": "A full-featured, hackable Next.js AI chatbot built by Vercel",
    "github_url": "https://github.com/vercel/chatbot",
    "owner": "vercel",
    "repository": "chatbot"
  }
]
```

## Common pitfalls

1. **No index** — most commands fail with "Run `vercel-templates index` first." Always index before searching.
2. **Semantic search without Ollama** — ensure Ollama is running and the chosen model is pulled.
3. **Stale index** — the catalog changes daily. Use the nightly workflow or run `vercel-templates index --reset` regularly.
4. **Wrong slug format** — slugs must contain `templates/`, e.g. `next.js/chatbot` or `/templates/next.js/chatbot`. Frameworks with dots (like `next.js`) must be preserved.

## Verification checklist

- [ ] `vercel-templates stats` returns a count greater than 0.
- [ ] `vercel-templates search "<query>"` returns relevant templates.
- [ ] If using semantic search, `curl http://localhost:11434/api/tags` responds.
- [ ] The MCP server responds to `tools/list` with the expected tools.
- [ ] `GET /health` on the REST API returns `{"status":"ok"}`.
