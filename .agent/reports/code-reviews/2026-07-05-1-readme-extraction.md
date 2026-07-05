# Code Review: [#1] Extract README text from Vercel detail pages

**Branch:** `feature/1-readme-extraction`  
**PR:** https://github.com/imKXNNY/vercel-templates-discovery/pull/15  
**Reviewer:** Jarvis (self-review)  
**Date:** 2026-07-05

## Summary

Implementation adds Next.js RSC flight-deferred chunk parsing for README extraction, plus improved install-command selection. All acceptance criteria met. No blockers.

## Findings

### 🔴 Blocker
- None

### 🟠 High
- None

### 🟡 Medium
- **MSYS-local lint/type tooling unavailable:** `ruff` and `mypy` could not be installed due to missing native wheels/build deps. Mitigation: CI workflow runs them on Ubuntu; local verification used `pytest` and `py_compile` instead. This should be re-run via GitHub Actions before merge.

### 🟢 Low / Nit
- Consider adding a broader integration test with a captured real HTML fixture once the project is moved to a Linux/WSL environment.
- `docs/PROJECT_STATUS.md` is useful but duplicates some planning info; acceptable for now.

## Correctness & Safety
- Edge cases handled: missing `readmeText`, malformed payload, missing GitHub URL, fallback regexes preserved.
- No secrets committed.

## Architecture & Maintainability
- New `_extract_flight_chunk` and `_unescape_json_string` helpers are cohesive and well-scoped.
- Install command selection logic is centralized in `_select_install_command`.

## Tests
- 6 unit tests added/passing in `tests/test_scraper.py`.
- Regression coverage for flight-chunk parsing and command selection.

## Verification commands

```bash
python -m pytest tests/test_scraper.py      # 6 passed
python -m py_compile vercel_templates/*.py  # success
python -m vercel_templates.cli index        # 284 templates indexed
```

## Review Gate Result

**Gate:** Review  
**Status:** PASS  
**Evidence:**
- Verdict: APPROVE
- Findings: 0 Blocker / 0 High / 1 Medium / 2 Low
- Report path: `.agent/reports/code-reviews/2026-07-05-1-readme-extraction.md`
- Tests: `pytest tests/test_scraper.py` → 6 passed
- Index verification: 284 templates, 82.4% with README, 100% with install command
**Next:** proceed
