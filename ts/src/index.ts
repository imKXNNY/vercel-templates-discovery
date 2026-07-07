export { VercelTemplateScraper, type ScraperOptions } from "./scraper.js";
export { TemplateDatabase } from "./db.js";
export { MCPServer, main } from "./mcp-server.js";
export type { Template, TemplateInput, DiscoveredTemplate } from "./types.js";
export {
  OllamaEmbeddingModel,
  FakeEmbeddingModel,
  getModel,
  embeddingText,
  normalize,
  EMBEDDING_MODEL,
  OLLAMA_URL,
  DIMENSIONS,
} from "./embeddings.js";
export type { EmbeddingModel } from "./types.js";
