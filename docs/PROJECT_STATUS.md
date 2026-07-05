# Project Owner Status: Vercel Templates Discovery

**Owner:** Jarvis (Windows Desktop Hermes)  
**Repo:** https://github.com/imKXNNY/vercel-templates-discovery (private)  
**Last updated:** 2026-07-05

## Mission

Build the standard agentic discovery layer for Vercel Templates — a searchable, always-up-to-date catalog that AI agents and developers can query to find the best starting point for any project.

## Current state (v0.2.0)

- Working CLI indexes the full Vercel Templates gallery (~284 templates)
- SQLite cache with FTS5 keyword search
- Extracts title, description, GitHub URL, owner, repo, install command
- **README extraction implemented (Issue #1):**
  - 234/284 templates (82.4%) have non-empty `readme_text`
  - 100% have an install command
  - Next.js RSC flight deferred chunks are parsed and JSON-unescaped
- **MCP server implemented (Issue #4):** exposes `search_templates`, `get_template`, `list_categories` via stdio JSON-RPC
- **TypeScript / WSL port implemented (Issue #7):**
  - Complete Node.js/TypeScript implementation under `ts/`
  - Feature parity with Python CLI: index, search, show, stats
  - MCP server with spec-compliant stdio JSON-RPC framing
  - Tests pass in WSL; `typecheck:all` covers src + tests + scripts
  - Open PR: https://github.com/imKXNNY/vercel-templates-discovery/pull/new/feature/7-typescript-port
- JSON output for agent consumption
- CI, tests, README, CONTRIBUTING guide
- ADOS framework adopted at repo layer
- 5 milestones and 14 roadmap issues created

## Priority backlog (next-best actions)

1. **Merge TypeScript port PR** (#7) — pending Kenny review / auto-merge
2. **Semantic search** (#11) — intent-based discovery
3. **PyPI / npm publish** (#8, #9) — frictionless adoption
4. **ToS review** (#13) — gating public release

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

- Issue #7 is implemented and pushed as `feature/7-typescript-port`. Review/merge is the next step.
- Remaining open backlog: 13 issues. Top candidates: semantic search (#11), PyPI/npm packaging (#8, #9), or ToS review (#13).
- The other open PR and 3 active branches should be reconciled before merging #7 to avoid conflicts.
