# ADOS Review Gate Report — TypeScript port (Issue #7)

## Summary

The TypeScript port replicates the existing Python scraper/CLI/MCP architecture in Node.js with strict typing, a separate database module, and helper coverage via unit tests. It compiles cleanly, but the full verification suite is blocked on Windows because `better-sqlite3` ships an invalid native binary in this environment, causing both `npm test` and `npx tsx src/cli.ts stats` to fail at runtime. A few code-quality issues remain, including a missing `framework` field in save data and fragile heuristics in HTML extraction, but these are individually fixable and do not prevent runtime behavior once the native dependency is usable.

## Findings

### 🔴 Blocker

- **`ts/package.json` / `ts/src/db.ts`**: `better-sqlite3` native binary is not a valid Win32 application on this Windows host, so `npm test` and the CLI fail at module load. This blocks verification of the port in this environment. However, this is a **build/runtime environment issue**, not a source-code defect. On a supported OS with rebuild tools the binary will work.
- **`ts/src/scraper.ts:138`**: `enrichTemplate` sets `data.framework = frameworks || category || ""`, but `saveTemplates` in `db.ts` does **not** write a `framework` column separately; the schema only has a `framework` column. `data.framework` is inserted into the templates table as `@framework` (line 62), so the fallback is actually preserved. However, the Python original writes `frameworks` twice and never stores `framework` as a separate concept. The TypeScript code correctly stores the `framework` concept, but the naming collision means the field is inconsistent across categories. **Suggested fix**: align with the original behavior or clarify what `framework` means in the schema/types; remove the duplicate semantics if not needed.
- **`ts/src/scraper.ts:156-158`**: The post-data fallback `if (category && FRAMEWORK_CATEGORIES.has(category) && !data.frameworks)` sets `data.frameworks = category`. Then line 159 runs `selectInstallCommand` using the already-assigned `frameworks`. In `index()` at line 188-191 the same logic is duplicated, but the first assignment inside `enrichTemplate` is the one that matters. This is not a bug, but it is redundant and could drift. **Suggested fix**: remove the duplicate logic in `index()` and pass `category` into `selectInstallCommand` rather than mutating `data.frameworks` twice.

### 🟠 High

- **`ts/src/scraper.ts:67-69`**: The discovery regex is extremely fragile and depends on exact Vercel HTML ordering. The Python version used the same regex, so this is parity behavior, but it is still a high risk for silent breakage. **Suggested fix**: add a smoke test or a fallback when no cards are found for a category.
- **`ts/src/scraper.ts:175-206`**: The custom worker pool is a hand-rolled concurrency implementation. Race conditions are unlikely because `queue.shift()` and `active` decrements are single-threaded, but the pattern is error-prone. **Suggested fix**: use `Promise.all` over chunked arrays or `p-limit` to reduce concurrency complexity and avoid future off-by-one bugs.
- **`ts/src/db.ts:49-52`**: `reset()` drops the `search` virtual table first, then `templates`. This is correct because `fts5` tables hold rowid references, but it does not back up any data. **Suggested fix**: document that `index()` intentionally wipes data; this is parity with Python, so consider it a known behavior.
- **`ts/src/mcp-server.ts:9-15`**: `MCPServer` instantiates both `VercelTemplateScraper` and `TemplateDatabase`. Both open the same SQLite path, which on `better-sqlite3` is fine (multiple connections are okay), but `VercelTemplateScraper` already owns a `db`. This creates two separate DB objects and two WAL files. **Suggested fix**: have `MCPServer` use `scraper.db` (expose it) or accept a single `TemplateDatabase` instance to avoid double-opening the database.
- **`ts/tests/scraper.test.ts:15-17`**: `sampleFlightPayload` is declared but never used. **Suggested fix**: remove the unused variable or add a test that uses it.

### 🟡 Medium

- **`ts/src/mcp-server.ts:136-139`**: `tools/call` downcasts `req.params` to `Record<string, unknown>` without runtime validation. Malformed MCP client requests could throw TypeError at `params.name`. **Suggested fix**: validate that `req.params` is an object and contains `name` before casting.
- **`ts/src/mcp-server.ts:203-208`**: `send` uses `\n\n` instead of `\r\n\r\n`, which is technically non-compliant with the MCP/JSON-RPC over stdio spec. The parser accepts both, so it works, but the server-side writer should be spec-compliant. **Suggested fix**: write `Content-Length: ${len}\r\n\r\n`.
- **`ts/src/cli.ts:39`**: `console.log(\`  ${t.description.slice(0, 120)}...\`)` will print a trailing `...` even if the description is shorter than 120 characters. **Suggested fix**: conditionally append `...` only when the description is longer than 120 chars.
- **`ts/src/cli.ts:19`**: `index` concurrency option is parsed with `Number()` but not validated. A non-numeric string becomes `NaN` and is passed to `scraper.index`, which then becomes `Math.min(NaN, slugs.length)` returning `NaN`, causing the `for` loop to spawn 0 workers. **Suggested fix**: validate/parse `options.concurrency` with a fallback and an error message.
- **`ts/src/scraper.ts:46-48`**: Retries for 429/503 sleep `2^attempt * 1000` ms, but the final `throw` on other status codes does not include the URL or retry context. **Suggested fix**: include the URL in the thrown error for better diagnostics.
- **`ts/package.json`**: `main` points to `dist/index.js`, but `src/index.ts` does not exist in the changed files. **Suggested fix**: add `src/index.ts` or remove the `main` field if it is not intended to be used as a library.
- **`ts/tsconfig.json`**: `include` only covers `src/**/*.ts`, so `tests/**/*.ts` and `scripts/*.ts` are not included in the TypeScript project. This is fine for `vitest`/`tsx` but may cause editor/type-checker drift. **Suggested fix**: add a `tsconfig.test.json` or update `include` to include `tests` and `scripts` with separate `noEmit` checks.
- **`ts/src/scraper.ts:287`**: `unescapeHtml` is a thin wrapper around `he.decode`. It is exported for tests but not documented. **Suggested fix**: keep it, but consider whether the indirection adds value or should be removed.

### 🟢 Low / Nit

- **`ts/src/scraper.ts`**: No trailing newline. **Suggested fix**: add trailing newline to match POSIX conventions.
- **`ts/src/scraper.ts:141`**: Variable named `m` is terse. **Suggested fix**: rename to `githubMatch`.
- **`ts/src/config.ts:47-48`**: `userAgent` returns a constant string every call. Could be a constant export instead of a function. **Suggested fix**: make it a `const USER_AGENT` and keep `userAgent()` as a re-export for compatibility, or leave as-is if it mirrors Python.
- **`ts/src/db.ts`**: Missing final newline. **Suggested fix**: add newline.
- **`ts/src/types.ts`**: Fields are all declared as required strings, but `framework` and `frameworks` are semantically similar; consider clarifying or removing one. **Suggested fix**: document the difference in a comment or rename one.
- **`ts/src/cli.ts`**: `show` command uses `process.exit(1)` on missing template, but other commands do not explicitly exit on error. **Suggested fix**: consistent error handling across commands (e.g., return non-zero for all fatal errors).
- **`ts/src/mcp-server.ts:221`**: Module-level `main()` is invoked at import time, which is necessary for CLI execution but makes `mcp-server.ts` harder to test in isolation. **Suggested fix**: wrap in `if (import.meta.url === pathToFileURL(process.argv[1]).href)` guard, or split entry point from `MCPServer` class.

## Verdict

**REQUEST_CHANGES**

The code is coherent and matches the Python implementation, but the verification environment cannot run the full suite due to the native dependency. Several issues should be addressed before merge: the `framework`/`frameworks` duplication, the `MCPServer` double database connection, the CLI concurrency parsing bug, and MCP spec-compliant framing. I recommend fixing the Blocker/High issues and re-running the three verification commands on a supported platform (or after rebuilding the native module). Because the blocker is environmental rather than a code defect, the gate can pass once the native dependency is resolved and tests/CLI run successfully.

## Gate Result

**Gate:** Review
**Status:** FAIL
**Evidence:**
- `npx tsc --noEmit` → exit 0
- `npm test` → exit 1 (better-sqlite3 native binary invalid Win32 application)
- `npx tsx src/cli.ts stats` → exit 1 (same native binary error)
**Failure reason:** Verification blocked by a Windows-specific `better-sqlite3` native binary load failure; additionally, code has Medium/High correctness and maintainability issues before merge.
**Next:** revise
