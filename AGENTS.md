# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, Cursor, Copilot, Codex, OpenCode, Hermes, etc.) when working in this repository.

## Repository overview

`vercel-templates-discovery` is an unofficial, agent-friendly CLI and library for indexing, searching, and comparing the [Vercel Templates](https://vercel.com/templates) gallery. It ships in two runtimes:

- `vercel_templates/` — Python implementation (Typer CLI, FastAPI REST server, stdio MCP server, Ollama embeddings).
- `ts/` — TypeScript / Node implementation (Commander CLI, stdio MCP server, library exports).

Both implementations share the same SQLite cache schema and produce the same indexed catalog.

## Directory structure

```text
vercel_templates/          # Python package
├── scraper.py             # Crawler + SQLite cache
├── cli.py                 # Typer CLI
├── server.py              # FastAPI REST server
├── mcp_server.py          # stdio MCP server
├── embeddings.py          # Ollama + sqlite-vec semantic search
└── tests/                 # pytest tests

ts/                        # TypeScript / npm package
├── src/
│   ├── scraper.ts         # Crawler + SQLite cache
│   ├── db.ts              # Database queries
│   ├── cli.ts             # Commander CLI
│   ├── mcp-server.ts      # stdio MCP server
│   └── index.ts           # Library exports
└── tests/                 # vitest tests

skills/productivity/vercel-templates-discovery/   # Cross-agent skill (SKILL.md)
.github/workflows/         # CI/CD workflows
```

## Conventions

- **Python**: target Python 3.10+, format with `ruff`, type-check with `mypy`, test with `pytest`.
- **TypeScript**: target Node.js 20+, type-check with `tsc`, test with `vitest`.
- **Commits**: use conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `ci:`).
- **Skills**: keep `SKILL.md` under 500 lines; put long reference material in separate files under `references/` or `scripts/`.

## Common commands

```bash
# Python dev
uv run pytest tests/ -q
uv run mypy vercel_templates/
uv run ruff check vercel_templates/

# TypeScript dev
cd ts && npm test
cd ts && npm run typecheck
```

## Things to watch out for

- Slugs are stored in the database with a leading `/` (e.g. `/templates/next.js/chatbot`). The `get()` helpers accept both `/templates/next.js/chatbot` and `templates/next.js/chatbot` for shell portability.
- Semantic search requires Ollama or the `offline` extra for Python; the npm package bundles a fallback embedding model and logs a warning when Ollama is unavailable.
- The scraper parses public Vercel Templates pages; keep the `README.md` disclaimer up to date and do not claim official affiliation.

## Agent skill

A cross-agent skill is available at `skills/productivity/vercel-templates-discovery/SKILL.md`. It is published to [skills.sh](https://skills.sh) and can be installed via `npx skills add imKXNNY/vercel-templates-discovery`.
