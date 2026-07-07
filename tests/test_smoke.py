import re

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


def test_get_nonexistent(scraper):
    assert scraper.get("/templates/unknown") is None
