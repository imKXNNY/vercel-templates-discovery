import json
import sys
from typing import Any, Optional

from .scraper import VercelTemplateScraper


class MCPServer:
    """A minimal Model Context Protocol server over stdio."""

    def __init__(self) -> None:
        self.scraper = VercelTemplateScraper()

    def run(self) -> None:
        while True:
            message = self._read_message()
            if message is None:
                break
            self._handle(message)

    def _read_message(self) -> Optional[dict[str, Any]]:
        headers: dict[str, str] = {}
        while True:
            line = sys.stdin.readline()
            if not line:
                return None
            line = line.strip()
            if line == "":
                break
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()
        length = int(headers.get("Content-Length", 0))
        if not length:
            return None
        data = sys.stdin.read(length)
        if len(data) < length:
            return None
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            self._send_error(None, -32700, "Parse error")
            return None

    def _handle(self, message: dict[str, Any]) -> None:
        method = message.get("method")
        msg_id = message.get("id")
        if method == "initialize":
            self._send_response(
                msg_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "vercel-templates-discovery", "version": "0.1.0"},
                },
            )
        elif method == "notifications/initialized":
            return
        elif method == "tools/list":
            self._send_response(msg_id, {"tools": self._tools()})
        elif method == "tools/call":
            self._handle_tool_call(msg_id, message.get("params", {}))
        elif msg_id is not None:
            self._send_error(msg_id, -32601, "Method not found")

    def _tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "search_templates",
                "description": "Search the indexed Vercel Templates catalog by keyword.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "default": 10},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "get_template",
                "description": "Get full details for a single template by its slug.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "slug": {"type": "string", "description": "Template slug, e.g. /templates/next.js/chatbot"}
                    },
                    "required": ["slug"],
                },
            },
            {
                "name": "list_categories",
                "description": "List the available template categories/frameworks in the catalog.",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]

    def _handle_tool_call(self, msg_id: Any, params: dict[str, Any]) -> None:
        name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            if name == "search_templates":
                query = arguments.get("query", "")
                limit = arguments.get("limit", 10)
                results = self.scraper.search(query, limit=limit)
                self._send_tool_response(msg_id, results)
            elif name == "get_template":
                slug = arguments.get("slug", "")
                result = self.scraper.get(slug)
                self._send_tool_response(msg_id, result)
            elif name == "list_categories":
                templates = self.scraper.all_templates()
                categories: set[str] = set()
                for t in templates:
                    for fw in t.get("frameworks", "").split(", "):
                        if fw:
                            categories.add(fw)
                    for uc in t.get("use_cases", "").split(", "):
                        if uc:
                            categories.add(uc)
                self._send_tool_response(msg_id, sorted(categories))
            else:
                self._send_error(msg_id, -32602, f"Tool not found: {name}")
        except Exception as exc:
            self._send_error(msg_id, -32603, str(exc))

    def _send_tool_response(self, msg_id: Any, result: Any) -> None:
        content = [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
        self._send_response(msg_id, {"content": content, "isError": False})

    def _send_response(self, msg_id: Any, result: Any) -> None:
        if msg_id is None:
            return
        self._send({"jsonrpc": "2.0", "id": msg_id, "result": result})

    def _send_error(self, msg_id: Any, code: int, message: str) -> None:
        error = {"code": code, "message": message}
        if msg_id is None:
            self._send({"jsonrpc": "2.0", "error": error})
        else:
            self._send({"jsonrpc": "2.0", "id": msg_id, "error": error})

    def _send(self, message: dict[str, Any]) -> None:
        data = json.dumps(message, ensure_ascii=False)
        encoded = data.encode("utf-8")
        sys.stdout.buffer.write(f"Content-Length: {len(encoded)}\n\n".encode("utf-8"))
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()


def main() -> None:
    server = MCPServer()
    server.run()


if __name__ == "__main__":
    main()
