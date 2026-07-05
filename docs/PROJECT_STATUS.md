# Project Owner Status: Vercel Templates Discovery

**Owner:** Jarvis (Windows Desktop Hermes)  
**Repo:** https://github.com/imKXNNY/vercel-templates-discovery (private)  
**Last updated:** 2026-07-05

## Mission

Build the standard agentic discovery layer for Vercel Templates — a searchable, always-up-to-date catalog that AI agents and developers can query to find the best starting point for any project.

## Current state (v0.1.0 + Issue #1 in review)

- Working CLI indexes the full Vercel Templates gallery (~284 templates)
- SQLite cache with FTS5 keyword search
- Extracts title, description, GitHub URL, owner, repo, install command
- **README extraction now implemented (Issue #1):**
  - 234/284 templates (82.4%) have non-empty `readme_text`
  - 100% have an install command
  - Next.js RSC flight deferred chunks are parsed and JSON-unescaped
- JSON output for agent consumption
- CI, tests, README, CONTRIBUTING guide
- ADOS framework adopted at repo layer
- 5 milestones and 14 roadmap issues created

## Priority backlog (next-best actions)

1. **MCP server** (#4) — highest agent-impact
2. **WSL / TypeScript port** (#7) — solves Windows dependency pain
3. **Semantic search** (#11) — intent-based discovery
4. **PyPI / npm publish** (#8, #9) — frictionless adoption
5. **ToS review** (#13) — gating public release

## Decision log

- Stay private until M6 / ToS review complete.
- Use pure Python (requests + BeautifulSoup) for now; Crawl4AI failed on MSYS native deps.
- Nightly re-index cron keeps the local cache fresh.
- ADOS layer precedence: repo > ADOS_HOME > package fallback. Repo layer is active.

## Auto-maintenance

- Nightly: `vercel-templates-index-nightly` re-indexes the catalog at 04:00
- Weekly: `vercel-templates-owner-checkin` reviews issues, updates this file, and reports to Kenny

## Notes for next session

- Issue #1 (README extraction) is implemented and verified. Ready to merge after review gate.
- Next priority: Issue #4 (MCP server) or Issue #7 (WSL/TypeScript port).
- Lint/type-check tooling is blocked on MSYS native deps (ruff/mypy fail to build). Consider running CI on GitHub Actions or porting to WSL/TypeScript.
