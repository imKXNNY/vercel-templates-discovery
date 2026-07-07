# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `vercel-templates diff` command in Python and TypeScript to compare two templates side by side.
- Support for `--json` and `--fields` in the diff command.
- `vercel-templates recent` and `vercel-templates trending` commands in Python and TypeScript.
- REST endpoints `/templates/recent` and `/templates/trending`.
- MCP tools `list_recent_templates` and `list_trending_templates`.
- `--by-category` grouping for trending output.
- `vercel-templates recommend <stack>` command in Python and TypeScript.
- Scoring based on frameworks, use cases, databases, CSS, authentication, CMS, title, and description.
- `--require-all-frameworks` flag for strict framework matching.
- REST endpoint `/templates/recommend?stack=...`.
- MCP tool `recommend_templates`.

## [0.2.5] - 2026-07-07

### Added

- TypeScript semantic search parity with Python implementation.
- `semantic` CLI command and `--semantic` search flag in both Python and TypeScript.
- `--reset` flag for the `index` command in both Python and TypeScript.
- `search_templates_semantic` MCP tool in both Python and TypeScript.
- `ts/README.md` and `ts/LICENSE` so the npm package shows documentation and license.
- Root `LICENSE` file (MIT).
- Docker image and `.github/workflows/docker.yml` for building/pushing to ghcr.io.
- Nightly re-index workflow and seed `catalog.json`.
- Hermes skill at `skills/productivity/vercel-templates-discovery/`.

### Changed

- Bumped default Ollama embedding model to `nomic-embed-text-v2-moe:latest`.
- Improved Ollama error messages with actionable URL hints.
- Distance scores are now shown in semantic search CLI output.

### Fixed

- Release workflow race conditions: added concurrency group and npm version-existence check.
- npm version mismatch that caused `v0.2.4` publish to fail.

## [0.2.4] - 2026-07-07

### Added

- `sqlite-vec` vector table and semantic search in Python.
- `nomic-embed-text-v2-moe:latest` embedding model via Ollama with fake fallback.
- `GET /templates/semantic` REST endpoint.
- Tag-based release workflow for PyPI and npm.

## [0.2.3] - 2026-07-06

### Added

- TypeScript port of the scraper, CLI, database, and MCP server.
- npm package `@imkxnny/vercel-templates-discovery`.

## [0.2.0] - 2026-07-05

### Added

- Python CLI: `index`, `search`, `show`, `export`, `stats`.
- SQLite + FTS5 cache.
- Detail page extraction for GitHub URL, install command, and metadata.
- REST API server and MCP server.
- PyPI package `vercel-templates-discovery`.

## [0.1.0] - 2026-07-04

### Added

- Initial project scaffold and category crawler.
- README, CONTRIBUTING, and CI workflow.
