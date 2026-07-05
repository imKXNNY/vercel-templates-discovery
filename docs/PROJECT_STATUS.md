# Project Owner Status: Vercel Templates Discovery

**Owner:** Jarvis (Windows Desktop Hermes)  
**Repo:** https://github.com/imKXNNY/vercel-templates-discovery (private)  
**Last updated:** 2026-07-05

## Mission

Build the standard agentic discovery layer for Vercel Templates — a searchable, always-up-to-date catalog that AI agents and developers can query to find the best starting point for any project.

## Current state (v0.2.0 in progress)

- Working CLI indexes the full Vercel Templates gallery (~284 templates)
- SQLite cache with FTS5 keyword search
- Extracts title, description, GitHub URL, owner, repo, install command
- **README extraction implemented (Issue #1):** 82.4% of templates have README text
- **MCP server implemented (Issue #4):** exposes `search_templates`, `get_template`, `list_categories` via stdio JSON-RPC
- JSON output for agent consumption
- CI, tests, README, CONTRIBUTING guide
- ADOS framework adopted at repo layer
- 5 milestones and 14 roadmap issues created

## Priority backlog (next-best actions)

1. **WSL / TypeScript port** (#7) — solves Windows dependency pain, enables better distribution
2. **Semantic search** (#11) — intent-based discovery
3. **PyPI / npm publish** (#8, #9) — frictionless adoption
4. **ToS review** (#13) — gating public release

## Decision log

- Stay private until M6 / ToS review complete.
- Use pure Python (requests + BeautifulSoup) for now; Crawl4AI failed on MSYS native deps.
- Nightly re-index cron keeps the local cache fresh.
- ADOS layer precedence: repo > ADOS_HOME > package fallback. Repo layer is active.
- Discord delivery not configured on native Windows Hermes; use chat for now.

## Auto-maintenance

- Nightly: `vercel-templates-index-nightly` re-indexes the catalog at 04:00
- Weekly: `vercel-templates-owner-checkin` reviews issues, updates this file, and reports to Kenny
- Daily: `vercel-templates-daily-update` (currently delivers to origin chat)

## Notes for next session

- Issue #4 (MCP server) is implemented and in review. Next priority: Issue #7 (WSL/TypeScript port).
