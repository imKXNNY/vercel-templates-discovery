import { createHash } from "node:crypto";
import type { EmbeddingModel } from "./types.js";

export const OLLAMA_URL =
  process.env.VTD_OLLAMA_URL ?? "http://localhost:11434/api/embed";
export const EMBEDDING_MODEL =
  process.env.VTD_EMBEDDING_MODEL ?? "nomic-embed-text-v2-moe:latest";
export const DIMENSIONS = 768;

export class OllamaEmbeddingModel implements EmbeddingModel {
  modelName: string;
  dimensions: number;
  ollamaUrl: string;
  timeout: number;

  constructor(
    modelName: string = EMBEDDING_MODEL,
    dimensions: number = DIMENSIONS,
    ollamaUrl: string = OLLAMA_URL,
    timeout: number = 30_000,
  ) {
    this.modelName = modelName;
    this.dimensions = dimensions;
    this.ollamaUrl = ollamaUrl;
    this.timeout = timeout;
  }

  async encode(texts: string[]): Promise<Float32Array[]> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    try {
      const resp = await fetch(this.ollamaUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: this.modelName,
          input: texts,
        }),
        signal: controller.signal,
      });
      if (!resp.ok) {
        throw new Error(
          `Ollama embedding request failed: ${resp.status} ${resp.statusText}`,
        );
      }
      const data = (await resp.json()) as { embeddings?: number[][] };
      const embeddings = data.embeddings ?? [];
      if (!embeddings.length) {
        throw new Error("Ollama returned no embeddings");
      }
      if (embeddings[0].length !== this.dimensions) {
        this.dimensions = embeddings[0].length;
      }
      return embeddings.map((arr) => new Float32Array(arr));
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        throw new Error(
          `Ollama embedding request timed out after ${this.timeout}ms. Is Ollama running at ${this.ollamaUrl}?`,
        );
      }
      throw new Error(
        `Ollama embedding request failed. Is Ollama running at ${this.ollamaUrl}? Error: ${err instanceof Error ? err.message : String(err)}`,
      );
    } finally {
      clearTimeout(timeoutId);
    }
  }

  async encodeSingle(text: string): Promise<Float32Array> {
    const results = await this.encode([text]);
    return results[0];
  }
}

export class FakeEmbeddingModel implements EmbeddingModel {
  modelName = "fake";
  dimensions: number;

  constructor(dimensions: number = DIMENSIONS) {
    this.dimensions = dimensions;
  }

  private vectorFor(text: string): Float32Array {
    const vec = new Float32Array(this.dimensions);
    const tokens = (text.toLowerCase().match(/\w+/g) ?? []) as string[];
    for (const token of tokens) {
      const rng = seededRandom(token);
      const dims = sampleWithoutReplacement(this.dimensions, 4, rng);
      for (const d of dims) {
        vec[d] += 1.0;
      }
    }
    let norm = 0.0;
    for (let i = 0; i < vec.length; i++) norm += vec[i] * vec[i];
    if (norm === 0) {
      const rng = seededRandom("__empty__");
      for (let i = 0; i < this.dimensions; i++) {
        vec[i] = rng.nextFloat();
      }
      norm = 0.0;
      for (let i = 0; i < vec.length; i++) norm += vec[i] * vec[i];
    }
    const scale = Math.sqrt(norm);
    for (let i = 0; i < vec.length; i++) {
      vec[i] = vec[i] / scale;
    }
    return vec;
  }

  async encode(texts: string[]): Promise<Float32Array[]> {
    return texts.map((t) => this.vectorFor(t));
  }

  async encodeSingle(text: string): Promise<Float32Array> {
    return this.vectorFor(text);
  }
}

export async function getModel(fake = false): Promise<EmbeddingModel> {
  if (fake) {
    return new FakeEmbeddingModel();
  }
  const model = new OllamaEmbeddingModel();
  try {
    await model.encodeSingle("hello");
    return model;
  } catch (err) {
    console.warn(
      `Ollama not reachable (${err instanceof Error ? err.message : String(err)}). Falling back to fake embeddings.`,
    );
    return new FakeEmbeddingModel();
  }
}

export function embeddingText(template: {
  title?: string;
  description?: string;
  frameworks?: string;
  use_cases?: string;
  css?: string;
  databases?: string;
  authentication?: string;
  cms?: string;
  readme_text?: string;
}): string {
  const parts = [
    template.title,
    template.description,
    template.frameworks,
    template.use_cases,
    template.css,
    template.databases,
    template.authentication,
    template.cms,
  ];
  const readme = (template.readme_text ?? "").slice(0, 2000);
  if (readme) parts.push(readme);
  return parts.filter((p): p is string => Boolean(p)).join(" ").trim();
}

export function normalize(vectors: Float32Array[]): Float32Array[] {
  return vectors.map((vec) => {
    let norm = 0.0;
    for (let i = 0; i < vec.length; i++) norm += vec[i] * vec[i];
    if (norm === 0) norm = 1.0;
    const scale = Math.sqrt(norm);
    const out = new Float32Array(vec.length);
    for (let i = 0; i < vec.length; i++) {
      out[i] = vec[i] / scale;
    }
    return out;
  });
}

function seededRandom(seed: string): { nextFloat: () => number } {
  let hash = createHash("sha256").update(seed).digest();
  let idx = 0;
  let a = 0;
  let b = 0;
  for (let i = 0; i < 4; i++) {
    a = (a << 8) | hash[i];
    b = (b << 8) | hash[i + 4];
  }
  a |= 1;
  b = (b % 2147483647) + 1;
  return {
    nextFloat: () => {
      a = (a * 16807) % 2147483647;
      b = (b * 48271) % 2147483646;
      idx += 1;
      hash = idx % 8 === 0
        ? createHash("sha256")
            .update(hash)
            .update(Buffer.from([idx & 0xff]))
            .digest()
        : hash;
      return (a + b) / (2147483647 + 2147483646);
    },
  };
}

function sampleWithoutReplacement(
  n: number,
  k: number,
  rng: { nextFloat: () => number },
): number[] {
  const selected = new Set<number>();
  while (selected.size < Math.min(k, n)) {
    selected.add(Math.floor(rng.nextFloat() * n));
  }
  return Array.from(selected);
}
