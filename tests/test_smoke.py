import re
import time

import pytest
import responses

from vercel_templates.config import BASE_URL
from vercel_templates.scraper import VercelTemplateScraper


@pytest.fixture
def scraper(tmp_path):
    return VercelTemplateScraper(delay=0.0, max_workers=2, db_path=str(tmp_path / "templates.db"))


DISCOVERY_HTML = """
<html><body>
<a data-template-card-wrapper href="/templates/next.js/chatbot">
  <h3>AI Chatbot</h3>
  <p class="line-clamp-2">A Next.js chatbot starter.</p>
</a>
</body></html>
"""

DETAIL_HTML = """
<html><body>
<h1>AI Chatbot</h1>
<p class="text-sm text-gray-900">A Next.js chatbot starter with streaming.</p>
<script>
self.__next_f.push([1, "\\\"githubUrl\\\":\\\"https://github.com/vercel/vercel/tree/main/examples/ai-chatbot\\\""]);
</script>
</body></html>
"""


def _mock_responses():
    responses.add(
        responses.GET,
        f"{BASE_URL}/templates/next.js",
        body=DISCOVERY_HTML,
        status=200,
        content_type="text/html",
    )
    responses.add(
        responses.GET,
        re.compile(rf"{re.escape(BASE_URL)}/templates/[^/]+/[^/]+"),
        body=DETAIL_HTML,
        status=200,
        content_type="text/html",
    )


@responses.activate
def test_index_full_flow(scraper):
    """Smoke test: mock discovery + detail pages and run a full index."""
    _mock_responses()

    import vercel_templates.scraper as scraper_module

    original_categories = scraper_module.DEFAULT_CATEGORIES
    scraper_module.DEFAULT_CATEGORIES = ["next.js"]
    try:
        count = scraper.index(concurrency=1)
    finally:
        scraper_module.DEFAULT_CATEGORIES = original_categories

    assert count == 1
    templates = scraper.all_templates()
    assert len(templates) == 1
    t = templates[0]
    assert t["slug"] == "/templates/next.js/chatbot"
    assert t["title"] == "AI Chatbot"
    assert "github_url" in t
    assert t["github_url"].startswith("https://github.com/")


@responses.activate
def test_search_after_index(scraper):
    """Smoke test: index and then keyword-search."""
    _mock_responses()

    import vercel_templates.scraper as scraper_module

    original_categories = scraper_module.DEFAULT_CATEGORIES
    scraper_module.DEFAULT_CATEGORIES = ["next.js"]
    try:
        scraper.index(concurrency=1)
    finally:
        scraper_module.DEFAULT_CATEGORIES = original_categories

    results = scraper.search("chatbot", limit=5)
    assert len(results) >= 1
    assert any("chatbot" in r["slug"].lower() for r in results)


def test_diff_templates(scraper):
    scraper._save_templates(
        [
            {
                "slug": "/templates/next.js/blog-a",
                "title": "Blog A",
                "description": "Minimal blog",
                "frameworks": "next.js",
                "github_url": "https://github.com/example/blog-a",
                "install_command": "npx create-next-app --example blog-a",
                "readme_text": "Blog A readme",
                "detail_url": "https://vercel.com/templates/next.js/blog-a",
                "indexed_at": 0,
            },
            {
                "slug": "/templates/next.js/blog-b",
                "title": "Blog B",
                "description": "Advanced blog",
                "frameworks": "next.js",
                "github_url": "https://github.com/example/blog-b",
                "install_command": "npx create-next-app --example blog-b",
                "readme_text": "Blog B readme",
                "detail_url": "https://vercel.com/templates/next.js/blog-b",
                "indexed_at": 0,
            },
        ]
    )
    a = scraper.get("/templates/next.js/blog-a")
    b = scraper.get("/templates/next.js/blog-b")
    assert a and b
    assert a["title"] != b["title"]
    assert a["frameworks"] == b["frameworks"]


def test_recently_added(scraper):
    now = int(time.time())
    scraper._save_templates(
        [
            {
                "slug": "/templates/next.js/new",
                "title": "New Template",
                "frameworks": "next.js",
                "framework": "next.js",
                "indexed_at": now - 3600,
                "detail_url": "",
            },
            {
                "slug": "/templates/next.js/old",
                "title": "Old Template",
                "frameworks": "next.js",
                "framework": "next.js",
                "indexed_at": now - 172800,
                "detail_url": "",
            },
        ]
    )
    recent = scraper.recently_added(hours=2, limit=10)
    assert len(recent) == 1
    assert recent[0]["slug"] == "/templates/next.js/new"


def test_trending_by_category(scraper):
    now = int(time.time())
    scraper._save_templates(
        [
            {
                "slug": "/templates/next.js/n1",
                "title": "N1",
                "frameworks": "next.js",
                "framework": "next.js",
                "indexed_at": now - 3600,
                "detail_url": "",
            },
            {
                "slug": "/templates/astro/a1",
                "title": "A1",
                "frameworks": "astro",
                "framework": "astro",
                "indexed_at": now - 7200,
                "detail_url": "",
            },
            {
                "slug": "/templates/next.js/o1",
                "title": "O1",
                "frameworks": "next.js",
                "framework": "next.js",
                "indexed_at": now - 172800,
                "detail_url": "",
            },
        ]
    )
    data = scraper.trending(hours=3, limit=10, by_category=True)
    assert data["total"] == 2
    grouped = data["grouped"]
    assert "next.js" in grouped
    assert "astro" in grouped
    assert len(grouped["next.js"]) == 1
    assert grouped["next.js"][0]["slug"] == "/templates/next.js/n1"
