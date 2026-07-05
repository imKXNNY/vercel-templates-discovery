# Plan: Issue #6 — Add REST server mode

## Goal
Provide a local HTTP API so non-CLI consumers (agents, web apps, other services) can query the indexed catalog.

## Approach
- Add a `serve` CLI command: `vercel-templates serve --host 127.0.0.1 --port 8000`.
- Use `fastapi` + `uvicorn` for the server.
- Endpoints:
  1. `GET /health` — server health
  2. `GET /templates` — list/search templates (query param `?q=...&limit=...`)
  3. `GET /templates/{slug}` — single template details
  4. `GET /categories` — list frameworks/use cases
- Reuse `VercelTemplateScraper` for data access.
- Add `fastapi` and `uvicorn` as optional dependencies under `server` extras in `pyproject.toml`, and include them in `dev` extras.
- Add tests using `httpx`/`TestClient`.

## Acceptance criteria
- [x] `vercel-templates serve` starts a working FastAPI server.
- [x] All four endpoints respond correctly.
- [x] `fastapi` and `uvicorn` in optional dependencies.
- [x] Tests cover endpoints with mocked/pre-populated DB.
- [ ] README updated with server usage.
- [ ] ADOS review gate passes.

## Files to modify
- `vercel_templates/server.py` (new)
- `vercel_templates/cli.py` (add `serve` command)
- `pyproject.toml` (add dependencies)
- `tests/test_server.py` (new)
- `README.md` (update)
- `docs/PROJECT_STATUS.md` (update)

## Dependencies
- Issue #2 (mocked tests) — patterns for isolated DB testing
- Issue #1 (README extraction) — already in place
