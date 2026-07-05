import os
import re

import responses

from vercel_templates.config import BASE_URL
from vercel_templates.scraper import (
    VercelTemplateScraper,
    _extract_install_command,
    _extract_readme_text,
)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def _load_fixture(name: str) -> str:
    with open(os.path.join(FIXTURES_DIR, name), encoding="utf-8") as f:
        return f.read()


@responses.activate
def test_discover_templates_mocked() -> None:
    scraper = VercelTemplateScraper(delay=0)
    responses.add(
        responses.GET,
        re.compile(re.escape(f"{BASE_URL}/templates/") + r".*"),
        body=_load_fixture("category_ai.html"),
        status=200,
        content_type="text/html",
    )

    templates = scraper.discover_templates()

    assert len(templates) == 2
    assert "/templates/eve/eve-chat-template" in templates
    assert "/templates/next.js/chatbot" in templates
    chatbot = templates["/templates/next.js/chatbot"]
    assert chatbot["title"] == "Chatbot"
    assert "Next.js AI chatbot" in chatbot["description"]
    assert chatbot["detail_url"] == f"{BASE_URL}/templates/next.js/chatbot"


@responses.activate
def test_enrich_template_mocked() -> None:
    scraper = VercelTemplateScraper(delay=0)
    responses.add(
        responses.GET,
        f"{BASE_URL}/templates/next.js/chatbot",
        body=_load_fixture("detail_chatbot.html"),
        status=200,
        content_type="text/html",
    )

    data = scraper.enrich_template("/templates/next.js/chatbot")

    assert data["title"] == "Chatbot"
    assert data["github_url"] == "https://github.com/vercel/chatbot"
    assert data["owner"] == "vercel"
    assert data["repository"] == "chatbot"
    assert "AI" in data["use_cases"].split(", ")
    assert "Authentication" in data["use_cases"].split(", ")
    assert "Next.js" in data["frameworks"].split(", ")
    assert "npx create-next-app --example chatbot my-app" in data["install_command"]
    assert "# Chatbot" in data["readme_text"]


def test_extract_readme_text_from_flight_chunk() -> None:
    scripts = 'JSS:7:{\\"readmeText\\":\\"$REF1\\"} other'
    scripts += 'REF1:1:{"key":"value"}'
    scripts += 'self.__next_f.push([1,"# Chatbot\\n\\nA test readme.\\n"])'
    text = _extract_readme_text(scripts)
    assert text is not None
    assert "# Chatbot" in text


def test_extract_install_command_from_readme() -> None:
    readme = "# Chatbot\n\n```bash\nnpx create-next-app --example chatbot my-app\n```\n"
    command = _extract_install_command(readme, "")
    assert command == "npx create-next-app --example chatbot my-app"


@responses.activate
def test_index_full_flow_mocked(tmp_path) -> None:
    scraper = VercelTemplateScraper(delay=0)
    # Override DB path so the test does not pollute the real cache
    scraper.db_path = str(tmp_path / "test.db")
    scraper._init_db()

    responses.add(
        responses.GET,
        f"{BASE_URL}/templates/next.js/chatbot",
        body=_load_fixture("detail_chatbot.html"),
        status=200,
        content_type="text/html",
    )
    responses.add(
        responses.GET,
        f"{BASE_URL}/templates/eve/eve-chat-template",
        body="<html><body><h1>eve Chat</h1></body></html>",
        status=200,
        content_type="text/html",
    )
    responses.add(
        responses.GET,
        re.compile(re.escape(f"{BASE_URL}/templates/") + r".*"),
        body=_load_fixture("category_ai.html"),
        status=200,
        content_type="text/html",
    )

    count = scraper.index(concurrency=1)
    assert count == 2

    results = scraper.search("chatbot")
    assert len(results) >= 1
    assert any(r["slug"] == "/templates/next.js/chatbot" for r in results)

    chatbot = scraper.get("/templates/next.js/chatbot")
    assert chatbot is not None
    assert chatbot["owner"] == "vercel"
