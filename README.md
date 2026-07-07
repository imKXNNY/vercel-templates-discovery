# Vercel Templates Discovery

[![PyPI](https://img.shields.io/pypi/v/vercel-templates-discovery)](https://pypi.org/project/vercel-templates-discovery/)
[![npm](https://img.shields.io/npm/v/@imkxnny/vercel-templates-discovery)](https://www.npmjs.com/package/@imkxnny/vercel-templates-discovery)
[![CI](https://github.com/imKXNNY/vercel-templates-discovery/actions/workflows/ci.yml/badge.svg)](https://github.com/imKXNNY/vercel-templates-discovery/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Discover, index, and search the [Vercel Templates](https://vercel.com/templates) gallery from your terminal or agent.

No public Vercel API exists — this tool builds a local, searchable catalog with install commands, metadata, and semantic search so you can find the right starter template in seconds.

## Quick start

Get the first search result in under a minute:

```bash
pip install vercel-templates-discovery
vercel-templates index
vercel-templates search "ai chatbot" --json
```

Example output:

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

## What you get

- **Search by keyword** — full-text search over titles, descriptions, frameworks, and use cases.
- **Search by intent** — semantic search with local embeddings (opt-in via Ollama).
- **Show details** — print GitHub URL, install command, README excerpt, and metadata for any template.
- **Compare templates** — diff two templates side by side by fields.
- **Recommend templates** — score templates against a stack or feature set.
- **Stay current** — nightly re-index workflow or `vercel-templates index --reset`.
- **Plug into agents** — MCP server, REST API, and cross-agent skill included.
- **Use it anywhere** — Python CLI, TypeScript CLI, local Docker build, or programmatic API.

## Installation

### Python (pip)

```bash
pip install vercel-templates-discovery
```

Requires Python 3.10+.

### TypeScript / Node (npm)

```bash
npm install -g @imkxnny/vercel-templates-discovery
```

Requires Node.js 20+.

### Docker

A Docker image is built automatically on tagged releases. To build locally before the first image is published:

```bash
docker build -t vercel-templates-discovery .
docker run --rm vercel-templates-discovery vercel-templates --help
```

To persist the index, mount a volume:

```bash
docker run --rm -v vercel-templates-cache:/root/.cache/vercel-templates \
  vercel-templates-discovery vercel-templates index
```

## Usage

### Index the catalog

```bash
vercel-templates index
```

### Keyword search

```bash
vercel-templates search "ai chatbot" --limit 3
vercel-templates search "ecommerce" --json
```

### Semantic search

```bash
pip install -e ".[semantic]"          # Python only; npm package includes sqlite-vec by default
vercel-templates semantic "AI chatbot" --limit 5
vercel-templates search "AI chatbot" --semantic
```

Semantic search requires a running Ollama instance (default: `http://localhost:11434`). See [Configuration](#configuration) for customization.

### Show details for a template

```bash
vercel-templates show /templates/next.js/chatbot
```

### Compare two templates

```bash
vercel-templates diff /templates/next.js/chatbot /templates/next.js/blog
```

### Get recommendations by stack

```bash
vercel-templates recommend "next.js, ai, tailwind"
```

### Export the catalog

```bash
vercel-templates export --output templates.json
vercel-templates export --output templates.json --include-readmes
```

The default export includes metadata only. Full READMEs are opt-in via `--include-readmes`.

### REST API server

```bash
vercel-templates serve
vercel-templates serve --host 0.0.0.0 --port 8080
```

Endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /templates?q=...&limit=...` | Keyword search |
| `GET /templates/semantic?q=...&limit=...` | Semantic search (requires `semantic` extra) |
| `GET /templates/recommend?stack=...` | Recommend by stack |
| `GET /templates/recent` | Recently added templates |
| `GET /templates/trending` | Trending templates |
| `GET /templates/{slug}` | Get one template by slug |
| `GET /categories` | List frameworks and use cases |

## Agent integration

### MCP server

Start the stdio MCP server (blocks and reads/writes JSON-RPC messages on stdin/stdout):

```bash
python -m vercel_templates.mcp_server
# or
vercel-templates-mcp
```

Tools exposed:

- `search_templates(query, limit)`
- `search_templates_semantic(query, limit)`
- `get_template(slug)`
- `list_categories()`
- `recommend_templates(stack, limit)`
- `list_recent_templates()`
- `list_trending_templates()`

Claude Desktop / Cursor config:

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

### Cross-agent skill (skills.sh)

A cross-agent skill is included in `skills/productivity/vercel-templates-discovery/` and is listed on [skills.sh](https://skills.sh). Install it into any compatible agent with:

```bash
npx skills add imKXNNY/vercel-templates-discovery --yes
```

Supported agents include Claude Code, Cursor, Copilot, Codex, OpenCode, and Hermes. The skill tells the agent how to invoke the CLI, REST API, and MCP server correctly.

### Hermes (manual install)

Copy or symlink the skill into your Hermes profile's `skills/` directory:

```bash
# Windows native Hermes
copy /Y skills\productivity\vercel-templates-discovery %LOCALAPPDATA%\hermes\skills\vercel-templates-discovery

# WSL / Linux / macOS
ln -s skills/productivity/vercel-templates-discovery ~/.hermes/profiles/default/skills/vercel-templates-discovery
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `VTD_OLLAMA_URL` | `http://localhost:11434/api/embed` | Ollama embeddings endpoint |
| `VTD_EMBEDDING_MODEL` | `nomic-embed-text-v2-moe:latest` | Embedding model name |

When you change the embedding model, existing vectors are no longer semantically compatible. Re-run `vercel-templates index --reset` before querying.

## Architecture

```text
vercel_templates/          # Python implementation
├── scraper.py             # crawler + SQLite cache
├── cli.py                 # Typer CLI
├── server.py              # FastAPI REST server
├── mcp_server.py          # stdio MCP server
└── embeddings.py          # Ollama + sqlite-vec semantic search

ts/                        # TypeScript / Node implementation
├── src/
│   ├── scraper.ts         # crawler + SQLite cache
│   ├── cli.ts             # Commander CLI
│   ├── mcp-server.ts      # stdio MCP server
│   └── index.ts           # library exports
└── tests/
```

The scraper parses Vercel's server-rendered pages and Next.js flight payloads to extract metadata, GitHub URLs, and install commands. The entire catalog can be rebuilt in under a minute.

## Project status

See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for the roadmap and [CHANGELOG.md](CHANGELOG.md) for release notes. Version 1.0.0 is released and available on [PyPI](https://pypi.org/project/vercel-templates-discovery/) and [npm](https://www.npmjs.com/package/@imkxnny/vercel-templates-discovery). A Docker image is built automatically for each tag and published to GitHub Container Registry once the repository is public.

## Feedback

This project is **unofficial and community-driven**. Feedback, ideas, and bug reports are very welcome:

- Open a [GitHub Issue](https://github.com/imKXNNY/vercel-templates-discovery/issues)
- Join the discussion on the [Vercel Community Showcase](https://community.vercel.com/t/community-tool-searchable-agent-friendly-vercel-templates-discovery-feedback-wanted/45314)

## Disclaimer

This is an **unofficial, community-maintained tool**. It is **not affiliated with, endorsed by, or sponsored by Vercel**. It is intended for personal research, local catalog building, and agent workflows. Please review Vercel's Terms of Service and use responsibly.

## License

MIT
