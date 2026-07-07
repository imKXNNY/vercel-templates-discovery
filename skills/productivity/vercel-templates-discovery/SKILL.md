---
name: vercel-templates-discovery
description: Use when you need to discover, search, or compare Vercel Templates for a project. Drives the local CLI, REST API, and MCP server shipped by the vercel-templates-discovery package.
version: 1.0.0
author: Kenny
license: MIT
metadata:
  hermes:
    tags: [vercel, templates, discovery, scaffolding, agentic]
    related_skills: [mcp, github]
---

# Vercel Templates Discovery

## Overview

The `vercel-templates-discovery` project provides a local, agent-friendly catalog of Vercel Templates. It can be installed as a Python package (PyPI), an npm package, or a Docker image. It exposes:

- A **CLI** (`vercel-templates`) for indexing, searching, and exporting templates.
- A **REST API** (`vercel-templates serve`) for HTTP-based queries.
- An **MCP server** (`vercel-templates-mcp`) that exposes tools to any MCP host.
- A **nightly refreshed JSON catalog** (`catalog.json`) committed to the repo.

This skill tells Hermes how to invoke those interfaces correctly.

## When to Use

- The user wants to find a Vercel Template for a specific framework or use case.
- The user asks "what templates exist for X?", "find me a starter for Y", or "compare Vercel templates".
- You need to bootstrap a project from a Vercel Template and need the install command.
- The user wants to keep the local template index up to date.

Do not use this skill when the user is asking about writing a new template from scratch or about Vercel deployment/configuration unrelated to templates.

## Installation Options

Choose the runtime the user already has:

```bash
# Python (with semantic search and server extras)
pip install "vercel-templates-discovery[server,semantic]"

# Node / npm
npm install -g @imkxnny/vercel-templates-discovery

# Docker (exposes REST API on port 8000)
docker run -p 8000:8000 -v vtd-data:/data ghcr.io/imkxnnycr.io/vercel-templates-discovery:latest
```

Note: Semantic search requires an Ollama instance reachable at `http://localhost:11434` by default. If Ollama is unavailable, the tool falls back to a fake embedding model and logs a warning.

## CLI Recipes

### Diff two templates

```bash
vercel-templates diff /templates/next.js/blog-a /templates/astro/blog-b
vercel-templates diff /templates/next.js/chatbot /templates/svelte/chatbot --json
```

### Index the catalog

```bash
vercel-templates index
```

Use `--reset` to drop the existing SQLite cache first:

```bash
vercel-templates index --reset
```

### Search

Keyword search (FTS5):

```bash
vercel-templates search "AI chatbot" --limit 10
```

Semantic search (requires Ollama and an existing index):

```bash
vercel-templates search "AI chatbot" --semantic --limit 10
vercel-templates semantic "authentication dashboard" --limit 5
```

### Show details

```bash
vercel-templates show /templates/next.js/chatbot --json
```

### Export catalog

```bash
vercel-templates export --output templates.json
```

### Serve REST API

```bash
vercel-templates serve --host 0.0.0.0 --port 8000
```

Endpoints:

- `GET /health` — health check
- `GET /templates?q=<query>&limit=<n>` — keyword search
- `GET /templates/semantic?q=<query>&limit=<n>` — semantic search
- `GET /templates/{slug}` — get a template by slug
- `GET /categories` — list categories

## MCP Server

Start the stdio MCP server:

```bash
vercel-templates-mcp
```

Available tools:

| Tool | Purpose |
|------|---------|
| `search_templates` | Keyword search |
| `search_templates_semantic` | Semantic search |
| `get_template` | Get details by slug |
| `list_categories` | List frameworks/use cases |

## Environment Variables

| Variable | Default | Effect |
|----------|---------|--------|
| `VTD_DB_PATH` | `<module_dir>/templates.db` | SQLite cache location |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama URL for embeddings |
| `VTD_EMBEDDING_MODEL` | `nomic-embed-text-v2-moe:latest` | Model name for Ollama |

## Common Pitfalls

1. **Semantic search without index** — `semantic` requires `index` to have run first. If no embeddings exist, results will be empty or fall back to keyword search depending on the caller.
2. **Ollama not running** — The Python CLI shows a clear error; the fake embedding model in Node/TS allows the tool to work but with degraded results.
3. **Stale index** — The catalog changes daily. Use the nightly workflow or run `vercel-templates index --reset` regularly.
4. **Wrong slug format** — Slugs must start with `/templates/`, e.g. `/templates/next.js/chatbot`.

## Verification Checklist

- [ ] The local index exists (`vercel-templates stats` returns a count > 0).
- [ ] Keyword search returns relevant templates.
- [ ] If using semantic search, Ollama is reachable.
- [ ] MCP server responds to `tools/list` and `tools/call`.
- [ ] REST API health endpoint returns `{"status":"ok"}`.
