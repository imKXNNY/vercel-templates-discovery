# Plan: Issue #3 — Add CHANGELOG.md

## Goal
Maintain a user-facing changelog following the Keep a Changelog format (https://keepachangelog.com/en/1.1.0/).

## Approach
- Add a `CHANGELOG.md` at the repo root.
- Include sections: Unreleased, 0.2.0, 0.1.0.
- List notable changes under Added/Changed/Fixed/Removed.
- Update `PROJECT_STATUS.md` to note changelog exists.

## Acceptance criteria
- [x] `CHANGELOG.md` exists and follows Keep a Changelog format.
- [x] Sections for 0.1.0, 0.2.0, and Unreleased.
- [x] Mentions README extraction, MCP server, TypeScript port, and test improvements.
- [ ] No spelling/formatting issues.

## Files to modify
- `CHANGELOG.md` (new)
- `docs/PROJECT_STATUS.md` (optional note)
