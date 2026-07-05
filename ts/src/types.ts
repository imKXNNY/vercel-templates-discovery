export interface TemplateInput {
  slug: string;
  framework: string;
  title: string;
  description: string;
  github_url: string;
  owner: string;
  repository: string;
  use_cases: string;
  frameworks: string;
  css: string;
  databases: string;
  authentication: string;
  cms: string;
  experimentation: string;
  readme_text: string;
  install_command: string;
  detail_url: string;
  indexed_at: number;
}

export type Template = TemplateInput & { id: number };

export interface DiscoveredTemplate {
  slug: string;
  framework: string;
  title: string;
  description: string;
  detail_url: string;
}

export interface JsonRpcRequest {
  jsonrpc: "2.0";
  id?: string | number;
  method: string;
  params?: unknown;
}

export interface JsonRpcResponse {
  jsonrpc: "2.0";
  id?: string | number;
  result?: unknown;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}
