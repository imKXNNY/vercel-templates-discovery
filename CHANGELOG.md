# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-07

### Added

- `vercel-templates recommend <stack>` command in Python and TypeScript.
- Scoring based on frameworks, use cases, databases, CSS, authentication, CMS, title, and description.
- `--require-all-frameworks` flag for strict framework matching.
- REST endpoint `/templates/recommend?stack=...`.
- MCP tool `recommend_templates` in Python and TypeScript MCP servers.
- `vercel-templates diff` command in Python and TypeScript to compare two templates side by side.
- Support for `--json` and `--fields` in the diff command.
- `vercel-templates recent` and `vercel-templates trending` commands in Python and TypeScript.
- REST endpoints `/templates/recent` and `/templates/trending`.
- MCP tools `list_recent_templates` and `list_trending_templates` in Python and TypeScript.
- `--by-category` grouping for trending output.
- Vercel ToS compliance review (`docs/VERCEL_TOS_REVIEW.md`).
- README disclaimer: unofficial, not affiliated with Vercel.
- `export` now supports `--include-readmes` to opt into full README text.

### Changed

- `export` defaults to metadata-only; full READMEs require `--include-readmes`.
- `catalog.json` redistributed without full README text to reduce copyright risk.
- Python and TypeScript versions bumped to `1.0.0`.

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
