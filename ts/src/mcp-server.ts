import { VercelTemplateScraper } from "./scraper.js";
import { TemplateDatabase } from "./db.js";
import type { JsonRpcRequest, JsonRpcResponse } from "./types.js";

interface MCPServerOptions {
  dbPath?: string;
}

export class MCPServer {
  private scraper: VercelTemplateScraper;
  private db: TemplateDatabase;

  constructor(options: MCPServerOptions = {}) {
    this.scraper = new VercelTemplateScraper({ dbPath: options.dbPath });
    this.db = new TemplateDatabase(options.dbPath);
  }

  run() {
    process.stdin.on("data", (chunk: Buffer) => {
      this.handleMessage(chunk.toString("utf-8"));
    });
    process.stdin.on("end", () => {
      this.close();
    });
  }

  private async handleMessage(raw: string) {
    const messages = this.parseMessages(raw);
    for (const req of messages) {
      const resp = await this.handleRequest(req);
      this.send(resp);
    }
  }

  private parseMessages(raw: string): JsonRpcRequest[] {
    const messages: JsonRpcRequest[] = [];
    let offset = 0;
    while (offset < raw.length) {
      const headers = new Map<string, string>();
      let headerEnd = raw.indexOf("\r\n\r\n", offset);
      if (headerEnd === -1) headerEnd = raw.indexOf("\n\n", offset);
      if (headerEnd === -1) break;

      const headerText = raw.slice(offset, headerEnd);
      for (const line of headerText.split(/\r?\n/)) {
        const [k, ...rest] = line.split(":");
        if (k && rest.length) headers.set(k.trim(), rest.join(":").trim());
      }

      const len = parseInt(headers.get("Content-Length") || "0", 10);
      const sepLen = raw.slice(headerEnd, headerEnd + 2) === "\r\n" ? 4 : 2;
      const bodyStart = headerEnd + sepLen;
      const body = raw.slice(bodyStart, bodyStart + len);
      offset = bodyStart + len;

      try {
        const parsed = JSON.parse(body) as JsonRpcRequest;
        messages.push(parsed);
      } catch {
        this.send({
          jsonrpc: "2.0",
          id: undefined,
          error: { code: -32700, message: "Parse error" },
        });
      }
    }
    return messages;
  }

  private async handleRequest(req: JsonRpcRequest): Promise<JsonRpcResponse> {
    const { id, method } = req;
    const error = (code: number, message: string): JsonRpcResponse => ({
      jsonrpc: "2.0",
      id,
      error: { code, message },
    });

    try {
      if (method === "initialize") {
        return {
          jsonrpc: "2.0",
          id,
          result: {
            protocolVersion: "2024-11-05",
            capabilities: { tools: {} },
            serverInfo: {
              name: "vercel-templates-discovery",
              version: "0.2.0",
            },
          },
        };
      }

      if (method === "tools/list") {
        return {
          jsonrpc: "2.0",
          id,
          result: {
            tools: [
              {
                name: "search_templates",
                description: "Search the Vercel Templates catalog",
                inputSchema: {
                  type: "object",
                  properties: {
                    query: { type: "string" },
                    limit: { type: "integer" },
                  },
                  required: ["query"],
                },
              },
              {
                name: "get_template",
                description: "Get details for a Vercel Template by slug",
                inputSchema: {
                  type: "object",
                  properties: {
                    slug: { type: "string" },
                  },
                  required: ["slug"],
                },
              },
              {
                name: "list_categories",
                description: "List template categories/frameworks",
                inputSchema: {
                  type: "object",
                  properties: {},
                },
              },
            ],
          },
        };
      }

      if (method === "tools/call") {
        const params = (req.params || {}) as Record<string, unknown>;
        const name = params.name as string;
        const args = (params.arguments || {}) as Record<string, unknown>;

        if (name === "search_templates") {
          const query = String(args.query || "");
          const limit = Number(args.limit || 10);
          const results = this.scraper.search(query, limit);
          return {
            jsonrpc: "2.0",
            id,
            result: {
              content: [
                { type: "text", text: JSON.stringify(results, null, 2) },
              ],
            },
          };
        }

        if (name === "get_template") {
          const slug = String(args.slug || "");
          const t = this.scraper.get(slug);
          return {
            jsonrpc: "2.0",
            id,
            result: {
              content: [
                {
                  type: "text",
                  text: t
                    ? JSON.stringify(t, null, 2)
                    : `Template not found: ${slug}`,
                },
              ],
            },
          };
        }

        if (name === "list_categories") {
          const rows = this.db.all();
          const categories = Array.from(
            new Set(rows.map((r) => r.frameworks).filter(Boolean)),
          ).sort();
          return {
            jsonrpc: "2.0",
            id,
            result: {
              content: [
                { type: "text", text: JSON.stringify(categories, null, 2) },
              ],
            },
          };
        }

        return error(-32601, `Tool not found: ${name}`);
      }

      return error(-32601, `Method not found: ${method}`);
    } catch (err) {
      return error(
        -32603,
        err instanceof Error ? err.message : String(err),
      );
    }
  }

  private send(resp: JsonRpcResponse) {
    const data = JSON.stringify(resp);
    const encoded = Buffer.from(data, "utf-8");
    process.stdout.write(`Content-Length: ${encoded.length}\n\n`);
    process.stdout.write(encoded);
  }

  close() {
    this.scraper.close();
    this.db.close();
  }
}

export function main() {
  const server = new MCPServer();
  server.run();
}

main();
