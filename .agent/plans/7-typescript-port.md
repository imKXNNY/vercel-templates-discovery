# Plan: Port core scraper to TypeScript / Node

## Issue
#7 — [M4] Port core scraper to TypeScript / Node

## Goal (1–2 sentences)

Re-implement the catalog scraper, SQLite cache, CLI, and MCP server in TypeScript / Node so the project can run on Windows without MSYS native-dependency issues and can be distributed as a single npm-compatible package.

## Acceptance Criteria

- [ ] A TypeScript project structure exists in a top-level `ts/` directory or as the new primary package layout.
- [ ] The scraper (`src/scraper.ts`) replicates the Python implementation:
  - category discovery via `/templates/<category>`
  - detail-page parsing for title, description, GitHub URL, install command, README text
  - Next.js RSC flight chunk extraction for `readme_text`
- [ ] The CLI (`src/cli.ts`) supports `index`, `search`, `show`, and `stats` with the same flags and JSON output.
- [ ] The SQLite cache (`src/db.ts`) uses `better-sqlite3` and preserves the same schema and FTS5 search behavior.
- [ ] The MCP server (`src/mcp-server.ts`) exposes `search_templates`, `get_template`, and `list_categories` over stdio JSON-RPC.
- [ ] Tests (`vitest` or `node:test`) cover scraper helpers, cache search, and MCP server.
- [ ] README and package.json updated with TypeScript setup / build / run instructions.
- [ ] A `build` script produces runnable JS in `dist/`.
- [ ] The Python implementation remains untouched until the TypeScript port is verified and merged.

## Branch

`feature/7-typescript-port`

## Plan file path

`.agent/plans/7-typescript-port.md`

## Risk / TDD classification

- **Risk:** medium. Porting from Python to TypeScript is straightforward but involves string/unescape differences, SQLite driver differences, and MCP framing.
- **TDD approach:** port existing tests first, then implement until they pass. Add one integration test that runs `npx tsx src/cli.ts index` and asserts on the database.

## Validation Contract (before implementation)

### Assertions
- [ ] `npm install` (or `pnpm install`) succeeds on WSL / Ubuntu.
- [ ] `npm run build` compiles `dist/` without errors.
- [ ] `npx tsx src/cli.ts stats` returns a count matching the Python index (±1 template due to upstream changes).
- [ ] `npx tsx src/cli.ts search chatbot --json` returns JSON results.
- [ ] `npx tsx src/cli.ts show /templates/next.js/chatbot --json` includes `readme_text` and `install_command`.
- [ ] `npx tsx src/mcp-server.ts` responds to JSON-RPC `tools/list`.
- [ ] `npm test` passes.

### Performance bounds
- Index run under 3 minutes on a typical connection.
- Search / tool response under 100ms.

### Interface contracts
- Same CLI interface as Python.
- Same MCP tool names and schemas.
- Same SQLite schema (templates table) so either implementation can read the same cache file.

## Implementation plan (slices)

1. **Bootstrap TypeScript project** (15 min)
   - `ts/`: `package.json`, `tsconfig.json`, `src/`, `tests/`
   - Dependencies: `typescript`, `tsx`, `vitest`, `commander`, `better-sqlite3`, `cheerio`, `node-fetch` (or native fetch).

2. **Port database layer** (20 min)
   - `src/db.ts`: open SQLite, create tables, insert/search templates.
   - Replicate FTS5 schema.

3. **Port HTTP utilities** (10 min)
   - `src/http.ts`: simple fetch with retry/backoff.

4. **Port scraper helpers** (30 min)
   - `src/scraper.ts`: category parsing, detail-page extraction, flight chunk unescape, install command synthesis.
   - Most work is regex/HTML extraction already proven in Python.

5. **Port CLI** (20 min)
   - `src/cli.ts`: `index`, `search`, `show`, `stats` using `commander`.

6. **Port MCP server** (20 min)
   - `src/mcp-server.ts`: stdio JSON-RPC, same tool set.

7. **Add tests** (25 min)
   - `tests/scraper.test.ts` and `tests/mcp-server.test.ts`.

8. **Update docs** (15 min)
   - Add TypeScript README section.
   - Update `docs/PROJECT_STATUS.md`.

9. **Verification and review gate** (15 min)
   - Run build, tests, integration checks.
   - Emit Gate Result block.

## Edge cases and failure handling

- `better-sqlite3` native build may fail on MSYS; this port is intended for WSL/Ubuntu/macOS where it works cleanly.
- Keep Python `vercel_templates/` as fallback; do not delete.
- If a flight chunk parse fails, return `null` for `readme_text` just like Python.

## Rollback considerations

- TypeScript port is additive. Python stays the default until TS is verified and merged.
- After verification, the repo can be reorganized to make TS the primary implementation, or both can coexist.
