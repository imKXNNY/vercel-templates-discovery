from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from vercel_templates.embeddings import FakeEmbeddingModel
from vercel_templates.scraper import VercelTemplateScraper
from vercel_templates.server import app, set_scraper


@pytest.fixture
def client(tmp_path) -> TestClient:
    pytest.importorskip("sqlite_vec")
    db_path = str(tmp_path / "test.db")
    model = FakeEmbeddingModel()
    scraper = VercelTemplateScraper(delay=0, embedding_model=model)
    scraper.db_path = db_path
    scraper._init_db()

    scraper._save_templates(
        [
            {
                "slug": "/templates/next.js/chatbot",
                "title": "Chatbot",
                "description": "A full-featured Next.js AI chatbot.",
                "frameworks": "Next.js",
                "use_cases": "AI, Authentication",
                "github_url": "https://github.com/vercel/chatbot",
                "owner": "vercel",
                "repository": "chatbot",
                "css": "",
                "databases": "",
                "authentication": "",
                "cms": "",
                "experimentation": "",
                "readme_text": "",
                "install_command": "",
                "detail_url": "",
                "indexed_at": 0,
            },
            {
                "slug": "/templates/next.js/blog",
                "title": "Blog Starter",
                "description": "A minimal blog",
                "frameworks": "Next.js",
                "use_cases": "blog",
                "github_url": "",
                "owner": "",
                "repository": "",
                "css": "",
                "databases": "",
                "authentication": "",
                "cms": "",
                "experimentation": "",
                "readme_text": "",
                "install_command": "",
                "detail_url": "",
                "indexed_at": 0,
            },
        ]
    )

    set_scraper(scraper)
    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_templates(client: TestClient) -> None:
    response = client.get("/templates")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    slugs = {r["slug"] for r in data}
    assert "/templates/next.js/chatbot" in slugs
    assert "/templates/next.js/blog" in slugs


def test_search_templates(client: TestClient) -> None:
    response = client.get("/templates?q=chatbot")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["slug"] == "/templates/next.js/chatbot"


def test_get_template(client: TestClient) -> None:
    response = client.get("/templates/next.js/chatbot")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "/templates/next.js/chatbot"
    assert data["owner"] == "vercel"


def test_get_template_not_found(client: TestClient) -> None:
    response = client.get("/templates/unknown/missing")
    assert response.status_code == 404


def test_list_categories(client: TestClient) -> None:
    response = client.get("/categories")
    assert response.status_code == 200
    data = response.json()
    assert "AI" in data
    assert "Next.js" in data


def test_search_semantic(client: TestClient) -> None:
    response = client.get("/templates/semantic?q=chatbot")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["slug"] == "/templates/next.js/chatbot"
