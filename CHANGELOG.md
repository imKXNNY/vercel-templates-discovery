# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Official Docker image published to GHCR (`ghcr.io/imkxnny/vercel-templates-discovery`).
- Multi-stage Dockerfile with Python 3.12 + Node 20, non-root user, and server extras.
- Missing `ts/tsconfig.json` for TypeScript builds.
- Mocked HTTP smoke tests for the scraper (`tests/test_scraper_mocked.py`).
- HTML fixtures for stable category-page and detail-page parsing tests.
- REST API server (`vercel-templates serve`) with FastAPI/uvicorn.
- `GET /health`, `/templates`, `/templates/{slug}`, and `/categories` endpoints.
- Hermes skill wrapper at `skills/vercel-templates/`.
- This `CHANGELOG.md`.
- Added `responses` and `httpx` to dev extras for HTTP mocking in tests.
- Added `fastapi` and `uvicorn` under `server` optional dependencies.
- Added `sqlite-vec` and `numpy` under a new `semantic` optional dependency for local vector search.
- Added `vercel_templates/embeddings.py` with Ollama-backed and fake embedding models.
- Added `sqlite-vec` embeddings table populated at index time when the `semantic` extra is installed.
- Added `semantic_search()` to `VercelTemplateScraper` using cosine similarity via `sqlite-vec`.
- Added `vercel-templates semantic` CLI command and `vercel-templates search --semantic` flag.
- Added `GET /templates/semantic` REST endpoint.
- Added MCP `search_templates_semantic` tool.
- Published to PyPI and npm (M4).
- Docker image with Python + TypeScript CLI (`Dockerfile`, `.dockerignore`, `publish-docker.yml`).

## [0.2.3] - 2026-07-06

### Fixed

- TypeScript build stage in Dockerfile now correctly copies `tsconfig.json` and `src/` before running `tsc`, enabling GHCR image builds.
- Added `declarationMap`, `sourceMap`, and `types: ["node"]` to `ts/tsconfig.json` for cleaner published TypeScript artifacts.
- Aligned TypeScript CLI `--version` output with package.json (0.2.3).

## [0.2.2] - 2026-07-06

### Added

- Manual `workflow_dispatch` trigger for `publish-docker.yml`.

### Changed

- Bumped package versions to `0.2.2` to align PyPI, npm, and Docker tags after the Docker workflow trigger fix.

## [0.2.1] - 2026-07-05

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
