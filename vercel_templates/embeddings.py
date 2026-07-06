from __future__ import annotations

import logging
import os
import re
from typing import Any, Protocol

import numpy as np

logger = logging.getLogger(__name__)

_OLLAMA_URL = os.getenv("VTD_OLLAMA_URL", "http://localhost:11434/api/embed")
_MODEL_NAME = os.getenv("VTD_EMBEDDING_MODEL", "nomic-embed-text-v2-moe:latest")
_DIMENSIONS = 768


class EmbeddingModel(Protocol):
    """Protocol for text embedding models."""

    model_name: str
    dimensions: int

    def encode(self, texts: list[str]) -> np.ndarray:
        """Encode a list of texts into a 2-D float32 array."""
        ...

    def encode_single(self, text: str) -> np.ndarray:
        """Encode a single text into a 1-D float32 array."""
        ...


class OllamaEmbeddingModel:
    """Embedding model backed by a local Ollama API."""

    def __init__(
        self,
        model_name: str = _MODEL_NAME,
        dimensions: int = _DIMENSIONS,
        ollama_url: str = _OLLAMA_URL,
        timeout: float = 30.0,
    ) -> None:
        self.model_name = model_name
        self.dimensions = dimensions
        self.ollama_url = ollama_url
        self.timeout = timeout

    def encode(self, texts: list[str]) -> np.ndarray:
        import requests

        try:
            resp = requests.post(
                self.ollama_url,
                json={"model": self.model_name, "input": texts},
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                "Ollama embedding request failed. Is Ollama running at "
                f"{self.ollama_url}? Error: {exc}"
            ) from exc
        data = resp.json()
        embeddings = data.get("embeddings", [])
        if not embeddings:
            raise RuntimeError("Ollama returned no embeddings")
        vectors = np.asarray(embeddings, dtype=np.float32)
        if vectors.shape[1] != self.dimensions:
            self.dimensions = vectors.shape[1]
        return vectors

    def encode_single(self, text: str) -> np.ndarray:
        result = self.encode([text])
        return np.asarray(result[0], dtype=np.float32)


class FakeEmbeddingModel:
    """Deterministic fake model for tests and CI.

    Vectors are derived from token frequencies in the text, so queries that
    share tokens with a template receive higher cosine similarity. This makes
    tests deterministic and semantically meaningful without a real embedding
    backend.
    """

    def __init__(self, dimensions: int = _DIMENSIONS) -> None:
        self.model_name = "fake"
        self.dimensions = dimensions

    def _vector_for(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dimensions, dtype=np.float32)
        tokens = re.findall(r"\w+", text.lower())
        for token in tokens:
            rng = np.random.default_rng(hash(token) % 2**32)
            dims = rng.choice(self.dimensions, size=4, replace=False)
            vec[dims] += 1.0
        if np.linalg.norm(vec) == 0:
            rng = np.random.default_rng(0)
            vec = rng.random(self.dimensions).astype(np.float32)
        vec /= np.linalg.norm(vec)
        return vec

    def encode(self, texts: list[str]) -> np.ndarray:
        return np.array([self._vector_for(t) for t in texts], dtype=np.float32)

    def encode_single(self, text: str) -> np.ndarray:
        return self._vector_for(text)


class SentenceTransformersEmbeddingModel:
    """Offline fallback using sentence-transformers (optional extra)."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._model = SentenceTransformer(self.model_name, device="cpu")
        self.dimensions = self._model.get_sentence_embedding_dimension()

    def encode(self, texts: list[str]) -> np.ndarray:
        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return np.asarray(embeddings, dtype=np.float32)

    def encode_single(self, text: str) -> np.ndarray:
        result = self.encode([text])
        return np.asarray(result[0], dtype=np.float32)


def get_model(fake: bool = False) -> EmbeddingModel:
    """Return the best available embedding model.

    Args:
        fake: Force the deterministic fake model.

    Returns:
        An EmbeddingModel instance. Falls back to FakeEmbeddingModel if Ollama
        is not reachable.
    """
    if fake:
        return FakeEmbeddingModel()
    try:
        model = OllamaEmbeddingModel()
        # Probe once to ensure Ollama is actually reachable.
        model.encode_single("hello")
        return model
    except Exception as exc:
        # Optional: try sentence-transformers fallback here if importable.
        logger.warning("Ollama not reachable (%s). Falling back to fake embeddings.", exc)
        return FakeEmbeddingModel()


def embedding_text(template: dict[str, Any]) -> str:
    """Build a single string of searchable text from a template record."""
    parts = [
        template.get("title", ""),
        template.get("description", ""),
        template.get("frameworks", ""),
        template.get("use_cases", ""),
        template.get("css", ""),
        template.get("databases", ""),
        template.get("authentication", ""),
        template.get("cms", ""),
    ]
    readme = template.get("readme_text", "")[:2000]
    if readme:
        parts.append(readme)
    return " ".join(p for p in parts if p).strip()


def normalize(vectors: np.ndarray) -> np.ndarray:
    """L2-normalize vectors along the last axis."""
    result = vectors.astype(np.float32)
    norms = np.linalg.norm(result, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return np.asarray(result / norms, dtype=np.float32)
