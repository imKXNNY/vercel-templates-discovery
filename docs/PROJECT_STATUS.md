# Project Owner Status: Vercel Templates Discovery

**Owner:** Jarvis (Windows Desktop Hermes)  
**Repo:** https://github.com/imKXNNY/vercel-templates-discovery (private)  
**Last updated:** 2026-07-05

## Mission

Build the standard agentic discovery layer for Vercel Templates — a searchable, always-up-to-date catalog that AI agents and developers can query to find the best starting point for any project.

## Current state (v0.2.1)

- Working CLI indexes the full Vercel Templates gallery (~284 templates)
- SQLite cache with FTS5 keyword search
- Extracts title, description, GitHub URL, owner, repo, install command
- **README extraction implemented (Issue #1):**
  - 234/284 templates (82.4%) have non-empty `readme_text`
  - 100% have an install command
  - Next.js RSC flight deferred chunks are parsed and JSON-unescaped
- **MCP server implemented (Issue #4):** exposes `search_templates`, `get_template`, `list_categories` via stdio JSON-RPC
- **TypeScript / WSL port implemented (Issue #7):** merged via PR #17
- **M2 deliverables implemented (Issues #2, #3):**
  - Mocked HTTP smoke tests with `responses` + HTML fixtures
  - `CHANGELOG.md` following Keep a Changelog format
- **M3 deliverables implemented (Issues #5, #6):**
  - Hermes skill wrapper at `skills/vercel-templates/`
  - REST API server (`vercel-templates serve`) with FastAPI/uvicorn endpoints
- **M4 deliverables implemented (Issues #8, #9):**
  - PyPI: `pip install vercel-templates-discovery` (v0.2.1)
  - npm: `npm install -g @imkxnny/vercel-templates-discovery` (v0.2.1)
- **M4 Docker image implemented (Issue #10):**
  - `docker run --rm ghcr.io/imkxnnny/vercel-templates-discovery:latest vercel-templates --help`
- JSON output for agent consumption
- CI, tests, README, CONTRIBUTING guide, CHANGELOG
- ADOS framework adopted at repo layer
- 5 milestones and 14 roadmap issues created

## Priority backlog (next-best actions)

1. **Docker image** (#10) — containerized distribution
2. **Semantic search** (#11) — intent-based discovery
3. **Template comparison** (#12) — compare/diff templates
4. **ToS review** (#13) — gating public release
5. **Public release v1.0.0** (#14) — final public polish

## Decision log

- Stay private until M6 / ToS review complete.
- Use pure Python (requests + BeautifulSoup) for now; Crawl4AI failed on MSYS native deps.
- TypeScript port targets WSL/Unix environments; Windows-native `better-sqlite3` builds are not supported on this host.
- Nightly re-index cron keeps the local cache fresh.
- ADOS layer precedence: repo > ADOS_HOME > package fallback. Repo layer is active.
- Discord delivery is now configured via home channel (#jarvis) on native Windows Hermes.

## Auto-maintenance

- Nightly: `vercel-templates-index-nightly` re-indexes the catalog at 04:00
- Weekly: `vercel-templates-owner-checkin` reviews issues, updates this file, and reports to Kenny
- Daily: `vercel-templates-daily-update` delivers to Discord home channel (#jarvis)

## Notes for next session

- Issue #7 is merged. Remaining open backlog: 13 issues. Next candidates: semantic search (#11), PyPI/npm packaging (#8, #9), or ToS review (#13).
