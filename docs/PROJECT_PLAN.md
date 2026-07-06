# Project Plan: Vercel Templates Discovery

## Vision

Become the standard agentic discovery layer for Vercel Templates — a searchable, always-up-to-date catalog that AI agents and developers can query to find the best starting point for any project.

## Current state (v0.1.0)

- [x] CLI that indexes the Vercel Templates gallery (~277 templates)
- [x] SQLite cache with FTS5 keyword search
- [x] Metadata extraction: title, description, GitHub URL, owner, repo, install command
- [x] JSON output for agent consumption
- [x] Private GitHub repo initialized
- [x] CI workflow with lint, type check, tests

## Milestones

### M1 — Foundation (done)
*Goal: a working CLI that indexes and searches the catalog.*

- [x] Category crawler
- [x] Detail page extractor
- [x] SQLite + FTS5 cache
- [x] CLI commands: `index`, `search`, `show`, `export`, `stats`
- [x] Git repo, `.gitignore`, README, CONTRIBUTING

### M2 — Data quality & robustness
*Goal: extract more value and survive Vercel UI changes.*

- [ ] Extract full README text from detail pages
- [ ] Add retry / backoff / rate-limit handling
- [ ] Add CLI smoke tests with mocked HTTP responses
- [ ] Improve framework/use-case/category classification
- [ ] Add CHANGELOG.md

### M3 — Agent integration
*Goal: make the tool trivial for AI agents to use.*

- [ ] MCP server exposing `search_templates`, `get_template`, `list_categories`
- [ ] Hermes skill wrapper
- [ ] OpenAPI/REST server mode
- [ ] Publish JSON catalog as a release artifact

### M4 — Portability & distribution
*Goal: easy install everywhere, including WSL/Windows.*

- [ ] Port core scraper to TypeScript / Node
- [ ] PyPI package
- [ ] npm package
- [ ] Docker image
- [ ] Nightly GitHub Actions re-index that commits the JSON catalog

### M5 — Advanced discovery
M5 roadmap has begun:

- [x] Semantic search with embeddings (Python)
  - [x] `sqlite-vec` + `numpy` under `semantic` extra
  - [x] Ollama-based embedding model (`nomic-embed-text-v2-moe:latest`)
  - [x] Vector table populated at index time
  - [x] CLI `semantic` command and `search --semantic` flag
  - [x] REST `GET /templates/semantic`
  - [x] MCP `search_templates_semantic` tool
- [ ] Template recommendation by stack / features
- [ ] Diff / compare templates
- [ ] Trending / newly added templates

### M6 — Publish & community
*Goal: make the project public and maintainable.*

- [ ] Resolve README extraction and any legal/ToS concerns
- [ ] Public GitHub repo
- [ ] Release v1.0.0
- [ ] Documentation site

## Backlog (next-best todos)

1. **README extraction** — biggest data gap right now.
2. **MCP server** — biggest agent-impact next step.
3. **WSL / TypeScript port** — solves your native Windows dependency issue.
4. **Semantic search** — unlocks intent-based discovery.
5. **PyPI / npm publish** — makes adoption frictionless.
6. **GitHub Project views** — table, board, roadmap for tracking issues.
7. **Benchmark multi-modal embedding models** — evaluate `embeddinggemma` and `qwen3-embedding` via Ollama for future projects that benefit from image/text embeddings (see pending research subagents).

## Open questions

- Does Vercel's ToS allow scraping the templates gallery? (low risk for personal/local use, but review before public launch)
- Should the published JSON catalog live in this repo or a separate data repo?
- Do we want to support other platforms (Netlify, Cloudflare, AWS) in the future?

## Success metrics

- Index completeness: 100% of discoverable templates
- Search latency: <100ms for local FTS5 queries
- Agent success: agent can find a relevant template in <3 tries
- Maintenance: nightly re-index runs green
