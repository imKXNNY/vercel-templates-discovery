# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Mocked HTTP smoke tests for the scraper (`tests/test_scraper_mocked.py`).
- HTML fixtures for stable category-page and detail-page parsing tests.
- REST API server (`vercel-templates serve`) with FastAPI/uvicorn.
- `GET /health`, `/templates`, `/templates/{slug}`, and `/categories` endpoints.
- Hermes skill wrapper at `skills/vercel-templates/SKILL.md`.
- This `CHANGELOG.md`.
- Added `responses` and `httpx` to dev extras for HTTP mocking in tests.
- Added `fastapi` and `uvicorn` under `server` optional dependencies.

## [0.2.0] - 2026-07-05

### Added

- Complete Node.js/TypeScript implementation under `ts/` targeting WSL/Unix environments.
- TypeScript CLI parity with Python: `index`, `search`, `show`, `stats`.
- TypeScript MCP server with spec-compliant stdio JSON-RPC framing.
- TypeScript test coverage with `vitest` and `typecheck:all` for `src` + `tests` + `scripts`.
- README extraction from Next.js RSC flight chunks, yielding non-empty `readme_text` for ~82% of templates.
- MCP server exposing `search_templates`, `get_template`, and `list_categories` tools over stdio.
- `index` CLI command for full catalog re-indexing.
- `.gitignore` updated for Node/`ts/` artifacts.

### Changed

- Python code refactored to satisfy `ruff` and `mypy` strict-mode checks.
- `pyproject.toml` dev extras now include `types-requests` and `types-beautifulsoup4`.
- CLI export default argument now uses `str` instead of a mutable `Path` default.

### Fixed

- Python `mypy` strict errors around CLI return types, `Any` returns, and generic `tuple` typing.
- MCP smoke test now handles the empty-DB case correctly.

## [0.1.0] - 2026-07-04

### Added

- Initial Python CLI for discovering and searching Vercel Templates.
- `vercel-templates` entry point with `index`, `search`, `show`, `stats`, and `export` commands.
- SQLite cache with FTS5 keyword search.
- Extraction of title, description, GitHub URL, owner, repository, and install command.
- CI workflow with `ruff`, `mypy`, `pytest`, and coverage.
- `README.md`, `CONTRIBUTING.md`, and project planning under `.agent/`.
- ADOS framework adoption at the repo layer.
