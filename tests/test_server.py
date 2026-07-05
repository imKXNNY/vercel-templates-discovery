from __future__ import annotations

import sqlite3

import pytest
from fastapi.testclient import TestClient

from vercel_templates.scraper import VercelTemplateScraper
from vercel_templates.server import app, set_scraper


@pytest.fixture
def client(tmp_path) -> TestClient:
    db_path = str(tmp_path / "test.db")
    scraper = VercelTemplateScraper(delay=0)
    scraper.db_path = db_path
    scraper._init_db()

    conn = sqlite3.connect(scraper.db_path)
    conn.execute(
        "INSERT INTO templates (slug, title, description, frameworks, use_cases, github_url, owner, repository) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "/templates/next.js/chatbot",
            "Chatbot",
            "A full-featured Next.js AI chatbot.",
            "Next.js",
            "AI, Authentication",
            "https://github.com/vercel/chatbot",
            "vercel",
            "chatbot",
        ),
    )
    conn.execute(
        "INSERT INTO search (rowid, title, description, readme_text, tags) VALUES (?, ?, ?, ?, ?)",
        (1, "Chatbot", "A full-featured Next.js AI chatbot.", "", "AI, Authentication, Next.js"),
    )
    conn.commit()
    conn.close()

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
    assert len(data) == 1
    assert data[0]["slug"] == "/templates/next.js/chatbot"


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
