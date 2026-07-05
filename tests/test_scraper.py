import pytest

from vercel_templates.scraper import (
    VercelTemplateScraper,
    _extract_install_command,
    _extract_readme_text,
)


@pytest.fixture
def scraper(tmp_path):
    return VercelTemplateScraper(delay=0.0, max_workers=2)


def test_extract_github_url(scraper):
    text = '"githubUrl":"https://github.com/vercel/vercel/tree/main/examples/nextjs"'
    assert (
        scraper._extract_github_url(text)
        == "https://github.com/vercel/vercel/tree/main/examples/nextjs"
    )


def test_extract_install_command_prefers_scaffold_in_readme(scraper):
    readme = """
```bash
npm install
npx create-next-app --example blog-starter my-app
```
"""
    assert (
        _extract_install_command(readme, "") == "npx create-next-app --example blog-starter my-app"
    )


def test_extract_install_command_falls_back_to_generic(scraper):
    readme = """
```bash
pnpm install
npm run dev
```
"""
    assert _extract_install_command(readme, "") == "pnpm install"


def test_extract_readme_text_from_flight_chunk():
    payload = r'self.__next_f.push([1,"S1:{\"readmeText\":\"$7b\"}"])</script><script>self.__next_f.push([1,"7b:Td58,\""])</script><script>self.__next_f.push([1,"# Chatbot\\n\\nA chatbot template."])</script>'
    readme = _extract_readme_text(payload)
    assert readme is not None
    assert "# Chatbot" in readme
    assert "A chatbot template." in readme


def test_select_install_command_prefers_scaffold(scraper):
    t = {
        "slug": "/templates/next.js/nextjs-boilerplate",
        "github_url": "https://github.com/vercel/vercel/tree/main/examples/nextjs",
        "frameworks": "next.js",
    }
    assert (
        scraper._select_install_command(t, "npm run dev")
        == "npx create-next-app --example nextjs my-app"
    )


def test_select_install_command_keeps_extracted_scaffold(scraper):
    t = {
        "slug": "/templates/next.js/chatbot",
        "github_url": "https://github.com/vercel/chatbot",
        "frameworks": "ai",
    }
    assert (
        scraper._select_install_command(t, "git clone https://github.com/vercel/chatbot")
        == "git clone https://github.com/vercel/chatbot"
    )
