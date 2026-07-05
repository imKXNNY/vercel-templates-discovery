# Plan: Build MCP server for agent integration

## Issue
#4 — [M3] Build MCP server for agent integration

## Goal (1–2 sentences)

Expose the Vercel Templates Discovery catalog to AI agents through a Model Context Protocol (MCP) server with three tools: search templates, get a template by slug, and list categories.

## Acceptance Criteria

- [ ] A new package/script `vercel_templates.mcp_server` is added.
- [ ] The MCP server implements `search_templates(query, limit)`, `get_template(slug)`, and `list_categories()` tools.
- [ ] Each tool returns clean JSON with the same schema as the CLI JSON output.
- [ ] The server can be started with `python -m vercel_templates.mcp_server`.
- [ ] A simple client test verifies the server responds to MCP JSON-RPC requests.
- [ ] README is updated with MCP setup/usage instructions.
- [ ] No breaking changes to existing CLI behavior.

## Branch

`feature/4-mcp-server`

## Plan file path

`.agent/plans/4-mcp-server.md`

## Risk / TDD classification

- **Risk:** low-medium. MCP is JSON-RPC over stdio. Main risk is protocol framing and correct schema.
- **TDD approach:** write a simple MCP client test that sends JSON-RPC requests and asserts on tool responses.

## Validation Contract (before implementation)

### Assertions
- [ ] `python -m vercel_templates.mcp_server` starts and stays running.
- [ ] A test client can send `{\"jsonrpc\":\"2.0\",\"method\":\"tools/list\",...}` and receive a list containing `search_templates`, `get_template`, `list_categories`.
- [ ] A test client can send `tools/call` for `search_templates` with query `"chatbot"` and receive results.
- [ ] A test client can send `tools/call` for `get_template` with `slug` `"/templates/next.js/chatbot"` and receive a JSON result.
- [ ] CLI commands still pass: `vercel-templates stats`, `vercel-templates search chatbot --limit 3`.
- [ ] `pytest` passes (including new MCP tests).

### Performance bounds
- Tool responses under 200ms for local SQLite queries.

### Interface contracts
- MCP server uses stdio transport (default for agents).
- Tool input schema:
  - `search_templates`: `{ query: string, limit?: number }`
  - `get_template`: `{ slug: string }`
  - `list_categories`: `{}`
- Tool output is a JSON string in the MCP `content` array (text type).

## Implementation plan (slices)

1. **Research minimal MCP Python SDK** (10 min)
   - Prefer `mcp` package if it installs cleanly; otherwise implement a tiny stdio JSON-RPC handler.
   - Given MSYS native dependency issues, a minimal custom server may be more reliable than a heavy SDK.

2. **Design server architecture** (15 min)
   - Add `vercel_templates/mcp_server.py` with a `main()` entry point.
   - Use `VercelTemplateScraper` as the data backend.
   - Implement handlers for `initialize`, `initialized`, `tools/list`, `tools/call`.

3. **Implement MCP stdio server** (30 min)
   - Read JSON-RPC messages line-by-line from stdin.
   - Parse headers (`Content-Length`).
   - Dispatch to handlers.
   - Return responses with proper JSON-RPC IDs.

4. **Implement tool handlers** (20 min)
   - `search_templates`: call `scraper.search(query, limit)`.
   - `get_template`: call `scraper.get(slug)`.
   - `list_categories`: derive unique categories from `scraper.all_templates()` and return sorted list.

5. **Add tests** (20 min)
   - Create `tests/test_mcp_server.py`.
   - Start server in subprocess, send JSON-RPC, assert tool list and results.

6. **Update docs** (15 min)
   - Add MCP section to README.
   - Add usage example for Claude Desktop / Cursor / other MCP clients.

7. **Verification and review gate** (15 min)
   - Run tests, run CLI smoke tests, run `py_compile`.
   - Emit Gate Result block.

## Edge cases and failure handling

- Empty index: return empty results with a friendly message suggesting `vercel-templates index`.
- Invalid slug in `get_template`: return `null` with an error message.
- MCP initialization errors: return JSON-RPC error with code `-32600`.
- Malformed incoming message: log and return parse error.

## Rollback considerations

- This is an additive feature. No database or CLI changes. Rollback is removing the file and docs.
