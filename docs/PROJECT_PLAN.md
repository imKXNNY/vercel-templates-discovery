# Project Plan: Vercel Templates Discovery

## Vision

Become the standard agentic discovery layer for Vercel Templates — a searchable, always-up-to-date catalog that AI agents and developers can query to find the best starting point for any project.

## Current state (v0.2.5)

- [x] Python CLI that indexes the Vercel Templates gallery (~277 templates)
- [x] TypeScript CLI port with parity
- [x] SQLite cache with FTS5 keyword search + sqlite-vec semantic search
- [x] Metadata extraction: title, description, GitHub URL, owner, repo, install command, README text
- [x] JSON output for agent consumption
- [x] Public GitHub repo
- [x] CI workflow with lint, type check, tests
- [x] PyPI + npm packages published via tag-based release workflow
- [x] MCP server (Python + TypeScript)
- [x] REST API server (Python)
- [x] LICENSE + README for both packages

## Milestones

### M1 — Foundation (done)
*Goal: a working CLI that indexes and searches the catalog.*

- [x] Category crawler
- [x] Detail page extractor
- [x] SQLite + FTS5 cache
- [x] CLI commands: `index`, `search`, `show`, `export`, `stats`
- [x] Git repo, `.gitignore`, README, CONTRIBUTING

### M2 — Data quality & robustness (partially done)
*Goal: extract more value and survive Vercel UI changes.*

- [x] Extract README text from detail pages (best-effort from flight payload)
- [x] Add retry / backoff / rate-limit handling
- [x] Improve framework/use-case/category classification
- [ ] Add CHANGELOG.md
- [ ] Add CLI smoke tests with mocked HTTP responses

### M3 — Agent integration (partially done)
*Goal: make the tool trivial for AI agents to use.*

- [x] MCP server exposing `search_templates`, `get_template`, `list_categories`
- [x] MCP `search_templates_semantic` tool (Python + TypeScript)
- [x] OpenAPI/REST server mode
- [ ] Hermes skill wrapper
- [ ] Publish JSON catalog as a release artifact

### M4 — Portability & distribution (partially done)
*Goal: easy install everywhere, including WSL/Windows.*

- [x] Port core scraper to TypeScript / Node
- [x] PyPI package
- [x] npm package
- [x] Tag-based release workflow with race-condition guards
- [ ] Docker image
- [ ] Nightly GitHub Actions re-index that commits the JSON catalog

### M5 — Advanced discovery (partially done)
*Goal: unlock intent-based discovery.*

- [x] Semantic search with embeddings (Python + TypeScript)
- [x] Ollama-based embedding model (`nomic-embed-text-v2-moe:latest`) with fake fallback
- [x] Vector table populated at index time
- [x] CLI `semantic` command and `search --semantic` flag
- [x] REST `GET /templates/semantic`
- [x] MCP `search_templates_semantic` tool
- [ ] Template recommendation by stack / features
- [ ] Diff / compare templates
- [ ] Trending / newly added templates

### M6 — Publish & community (partially done)
*Goal: make the project public and maintainable.*

- [x] Public GitHub repo
- [x] Resolve README extraction (best-effort implemented)
- [ ] Review Vercel ToS concerns before public launch
- [ ] Release v1.0.0
- [ ] Documentation site

## Backlog (next-best todos)

1. **Docker image** — easiest remaining distribution win.
2. **Nightly re-index** — keeps catalog fresh automatically.
3. **JSON catalog release artifact** — lets agents fetch the catalog without scraping.
4. **Hermes skill wrapper** — native integration into your assistant stack.
5. **Template recommendation / diff / trending** — advanced discovery features.
6. **Benchmark multi-modal embedding models** — evaluate `embeddinggemma` and `qwen3-embedding` via Ollama for future projects that benefit from image/text embeddings.
7. **CHANGELOG.md + smoke tests** — project hygiene.

## Open questions

- Does Vercel's ToS allow scraping the templates gallery? (low risk for personal/local use, but review before public launch)
- Should the published JSON catalog live in this repo or a separate data repo?
- Do we want to support other platforms (Netlify, Cloudflare, AWS) in the future?

## Success metrics

- Index completeness: 100% of discoverable templates
- Search latency: <100ms for local FTS5 queries
- Agent success: agent can find a relevant template in <3 tries
- Maintenance: nightly re-index runs green
