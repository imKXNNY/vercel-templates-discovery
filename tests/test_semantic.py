import sqlite3

import numpy as np
import pytest

from vercel_templates.embeddings import FakeEmbeddingModel, OllamaEmbeddingModel, embedding_text


def test_semantic_extra_imports():
    pytest.importorskip("sqlite_vec")
    import numpy as np

    assert hasattr(np, "array")


def test_embedding_text_joins_fields():
    t = {
        "title": "Blog Starter",
        "description": "A minimal blog",
        "frameworks": "next.js",
        "use_cases": "blog",
        "readme_text": "# Blog Starter\n\nHello world.",
    }
    text = embedding_text(t)
    assert "Blog Starter" in text
    assert "next.js" in text
    assert "# Blog Starter" in text


def test_fake_embedding_dimensions():
    model = FakeEmbeddingModel(dimensions=768)
    vec = model.encode_single("hello")
    assert vec.shape == (768,)
    assert abs(1.0 - np.linalg.norm(vec)) < 1e-5


def test_fake_embeddings_are_detinistic_for_same_text():
    model = FakeEmbeddingModel()
    a = model.encode_single("foo")
    b = model.encode_single("foo")
    assert np.allclose(a, b)


def test_ollama_model_returns_normalized_768_vectors():
    pytest.importorskip("requests")
    model = OllamaEmbeddingModel()
    vec = model.encode_single("hello world")
    assert vec.shape == (768,)
    assert abs(1.0 - np.linalg.norm(vec)) < 1e-5


def test_vector_table_created():
    pytest.importorskip("sqlite_vec")
    from vercel_templates.scraper import VercelTemplateScraper

    scraper = VercelTemplateScraper()
    conn = sqlite3.connect(scraper.db_path)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    assert "embeddings" in tables
    conn.close()


def test_semantic_search_ranks_results():
    pytest.importorskip("sqlite_vec")
    from vercel_templates.embeddings import FakeEmbeddingModel
    from vercel_templates.scraper import VercelTemplateScraper

    model = FakeEmbeddingModel()
    scraper = VercelTemplateScraper(embedding_model=model)
    scraper._save_templates(
        [
            {
                "slug": "/templates/next.js/chatbot",
                "title": "AI Chatbot",
                "description": "A chatbot template powered by AI",
                "frameworks": "next.js",
                "use_cases": "ai, chatbot",
                "readme_text": "",
                "github_url": "",
                "owner": "",
                "repository": "",
                "css": "",
                "databases": "",
                "authentication": "",
                "cms": "",
                "experimentation": "",
                "install_command": "",
                "detail_url": "",
                "indexed_at": 0,
            },
            {
                "slug": "/templates/next.js/blog",
                "title": "Blog Starter",
                "description": "A minimal blog",
                "frameworks": "next.js",
                "use_cases": "blog",
                "readme_text": "",
                "github_url": "",
                "owner": "",
                "repository": "",
                "css": "",
                "databases": "",
                "authentication": "",
                "cms": "",
                "experimentation": "",
                "install_command": "",
                "detail_url": "",
                "indexed_at": 0,
            },
        ]
    )
    results = scraper.semantic_search("chatbot", limit=2)
    assert results[0]["slug"] == "/templates/next.js/chatbot"
