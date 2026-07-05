# Plan: Extract full README text from Vercel template detail pages

## Issue
#1 — [M2] Extract full README text from detail pages

## Goal (1–2 sentences)

Parse the Next.js RSC flight payload embedded in Vercel template detail pages so that the `readme_text` field is populated with the rendered README markdown, enabling richer search, agent context, and install-command extraction.

## Acceptance Criteria

- [ ] `readme_text` is non-empty for >= 80% of indexed templates after a full `vercel-templates index`.
- [ ] README text is returned as plain markdown (escaped sequences like `\\n`, `\\\"`, `\\*` are unescaped correctly).
- [ ] `vercel-templates show /templates/next.js/chatbot --json` returns a `readme_text` field containing the README content.
- [ ] The existing metadata extraction (title, description, GitHub URL, install command) continues to work.
- [ ] A unit test verifies README extraction on a mocked detail-page payload.
- [ ] No new external dependencies are introduced (stay within `requests`, `bs4`, stdlib).

## Branch

`feature/1-readme-extraction`

## Plan file path

`.agent/plans/1-readme-extraction.md`

## Risk / TDD classification

- **Risky logic:** parser/unescape logic and regex state machine for flight payload JSON.
- **TDD approach:** write a failing test first with a captured sample payload, then implement the parser until it passes.

## Validation Contract (before implementation)

### Assertions
- [ ] After `vercel-templates index`, `sqlite3` query shows `>= 80%` of rows have non-empty `readme_text`.
- [ ] `vercel-templates show /templates/next.js/chatbot --json` outputs a `readme_text` field with length > 100 characters.
- [ ] `pytest tests/test_scraper.py` passes, including the new README extraction test.
- [ ] `ruff check .` passes with zero errors.
- [ ] `mypy vercel_templates` passes with zero errors.

### Performance bounds
- Index time must not increase by more than 25% (baseline ~60s for 277 templates on current hardware).

### Interface contracts
- No CLI changes; the `readme_text` field already exists in the data model and JSON output.

## Implementation plan (slices)

1. **Capture sample payload** (5 min)
   - Fetch `/templates/next.js/chatbot` and `/templates/next.js/nextjs-boilerplate` and save the raw HTML for test fixtures.
   - Store under `tests/fixtures/` (do not commit live HTML if it contains sensitive data; use synthetic or stripped payloads).

2. **Understand the flight payload shape** (15 min)
   - Locate the `readmeText` key in the script payloads.
   - Determine how deeply escaped the value is and where it ends (escaped quotes, nested JSON).

3. **Implement robust README extractor** (30 min)
   - Add `_extract_readme_text_flight(payload: str) -> Optional[str]`.
   - Use a state machine or JSON-aware scan to extract the full `readmeText` string including escaped quotes and newlines.
   - Unescape the result to clean markdown.
   - Keep the existing fallback regexes as safety net.

4. **Wire into enrich_template** (10 min)
   - Replace call to `_extract_readme_text(scripts)` with the new extractor.
   - Ensure `install_command` extraction uses the now-populated `readme_text` first, then falls back to scripts.

5. **Add tests** (20 min)
   - Create `tests/test_readme_extraction.py` with a synthetic escaped flight payload.
   - Test markdown unescaping, empty fallback, and integration with `_extract_install_command`.

6. **Re-index and verify** (15 min)
   - Run `vercel-templates index --concurrency 4`.
   - Run verification queries against the SQLite cache.

7. **Self-review / ADOS review gate** (15 min)
   - Run `git diff --stat`, `ruff`, `mypy`, `pytest`.
   - Emit Gate Result block.

## Edge cases and failure handling

- `readmeText` missing or shorter than 200 chars: return empty string, fall back to old behavior.
- Malformed flight payload: catch exception, log warning, return empty string.
- HTML entity/unicode escapes: ensure `_unescape` handles `\uXXXX`, `\n`, `\t`, `\"