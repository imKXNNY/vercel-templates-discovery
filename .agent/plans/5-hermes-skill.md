# Plan: Issue #5 — Create Hermes skill wrapper

## Goal
Add a `vercel-templates` Hermes skill so agents can query the Vercel Templates catalog natively from within Hermes.

## Approach
- Add a `vercel-templates` skill directory under the Hermes skills path (repo-local `skills/` for now; user can symlink or copy to Hermes profile).
- The skill should expose a set of agent-friendly tools/commands:
  1. `search_templates(query, limit)` — keyword search via the catalog
  2. `get_template(slug)` — full details for a single template
  3. `list_categories()` — available frameworks/use cases
- Use the Python CLI via subprocess or import the `VercelTemplateScraper` module directly.
- Prefer direct module import for speed and testability; fallback to CLI subprocess if not installed.
- Provide a `SKILL.md` with frontmatter, description, and usage examples.

## Acceptance criteria
- [x] Skill directory exists at `skills/vercel-templates/`.
- [x] `SKILL.md` with proper frontmatter and tool descriptions.
- [x] A small wrapper script (`skills/vercel-templates/scripts/query.py`) that agents can call.
- [ ] Tests or smoke checks that the skill can query the catalog.
- [ ] README updated with Hermes skill installation instructions.

## Files to modify
- `skills/vercel-templates/SKILL.md` (new)
- `skills/vercel-templates/scripts/query.py` (new)
- `README.md` (update)
- `docs/PROJECT_STATUS.md` (update)

## Dependencies
- Issue #4 (MCP server) implemented — reuse scraper logic
- Issue #6 (REST server) optional — can be used as the backend later
