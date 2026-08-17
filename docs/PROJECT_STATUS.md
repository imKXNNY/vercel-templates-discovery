# Project Owner Status: Vercel Templates Discovery

**Owner:** Jarvis (Windows Desktop Hermes)  
**Repo:** https://github.com/imKXNNY/vercel-templates-discovery (private)  
**Last updated:** 2026-08-17

## Mission

Build the standard agentic discovery layer for Vercel Templates — a searchable, always-up-to-date catalog that AI agents and developers can query to find the best starting point for any project.

## Current state

- **Catalog:** 293 templates indexed (up from ~284)
- **CLI health:** `vercel-templates stats` and `vercel-templates index -c 2` both pass
- **Test health:** `pytest` — 35 passed, 1 deprecation warning (Starlette/httpx)
- **Branch:** `master` is now the source of truth; the old `chore/repo-security-hardening` local branch was stale and its remote was removed, so work was stashed and master was fast-forwarded
- **GitHub hygiene:** Issue templates, CODEOWNERS, and PR template landed on master via fast-forward
- **Open issues:** 1 — #21 (ADOS workflow-pack idea), unassigned, no milestone
- **Milestones M2–M6:** 0 open issues each; all previously tracked items are closed

## Priority backlog (next-best actions)

1. **Scope the ADOS workflow-pack (#21)** — turn the rough idea into concrete, reusable agentic workflows. Draft a design doc and split out the first implementable workflow.
2. **Address pytest deprecation warning** — install `httpx` >= 0.28 (Starlette now prefers `httpx` over the older `requests`-based test client) or pin the test client dependency.
3. **Consider a patch release** — catalog grew ~3%; if README/install-command coverage changed materially, publish v0.2.4.

## Decision log

- Stay private until M6 / ToS review complete.
- Use pure Python (requests + BeautifulSoup) for now; Crawl4AI failed on MSYS native deps.
- TypeScript port targets WSL/Unix environments; Windows-native `better-sqlite3` builds are not supported on this host.
- Nightly re-index cron keeps the local cache fresh.
- ADOS layer precedence: repo > ADOS_HOME > package fallback. Repo layer is active.
- Discord delivery is now configured via home channel (#jarvis) on native Windows Hermes.
- `PYTHONPATH` must be cleared when invoking `uv run` on native Windows, otherwise the Hermes venv numpy (cp311) leaks into the project venv (cp312) and crashes the CLI.

## Auto-maintenance

- Nightly: `vercel-templates-index-nightly` re-indexes the catalog at 04:00
- Weekly: `vercel-templates-owner-checkin` reviews issues, updates this file, and reports to Kenny
- Daily: `vercel-templates-daily-update` delivers to Discord home channel (#jarvis)

## Notes for next session

- Issue #21 is the only open item. It is still an idea, not a spec — the highest-value next step is to turn it into a concrete workflow-pack design.
- No blockers. Safe to proceed with #21 scoping and the httpx warning cleanup.
