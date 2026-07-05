# Plan: Issue #2 — Add CLI smoke tests with mocked HTTP responses

## Goal
Add deterministic, fast unit tests that exercise the `VercelTemplateScraper` category crawler and detail extractor without making real HTTP requests.

## Approach
- Use `responses` library to mock GET requests to `vercel.com/templates/{category}` and `vercel.com/templates/{slug}`.
- Capture minimal real HTML fixtures for one category page and one detail page, then strip/sanitize to stable fixtures.
- Add tests for:
  1. `discover_templates()` returns at least one template with slug/title/description from a mocked category page.
  2. `enrich_template()` extracts github_url, owner, repository, frameworks, use_cases, and install_command from a mocked detail page.
  3. `_extract_readme_text()` and `_extract_install_command()` helpers via direct fixtures.

## Acceptance criteria
- [x] New tests in `tests/test_scraper_mocked.py`.
- [x] `responses` is installed via `pyproject.toml` dev extras.
- [ ] All Python tests pass locally and in CI.
- [x] No real network traffic during tests.

## Files to modify
- `tests/test_scraper_mocked.py` (new)
- `tests/fixtures/category_ai.html` (new)
- `tests/fixtures/detail_chatbot.html` (new)
- `pyproject.toml` (ensure `responses` is present) — already present

## Dependencies
- Issue #1 already in place (README extraction functions used in tests)
- `responses` library
