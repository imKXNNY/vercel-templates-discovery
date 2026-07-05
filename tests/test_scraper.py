import pytest
from vercel_templates.scraper import VercelTemplateScraper


@pytest.fixture
def scraper(tmp_path):
    return VercelTemplateScraper(delay=0.0, max_workers=2)


def test_extract_github_url(scraper):
    text = '\"githubUrl\":\"https://github.com/vercel/vercel/tree/main/examples/nextjs\"'
    assert scraper._extract_github_url(text) == "https://github.com/vercel/vercel/tree/main/examples/nextjs"


def test_synthesize_install_command_nextjs_example(scraper):
    t = {
        "slug": "/templates/next.js/nextjs-boilerplate",
        "github_url": "https://github.com/vercel/vercel/tree/main/examples/nextjs",
        "frameworks": "next.js",
    }
    assert scraper._synthesize_install_command(t) == "npx create-next-app --example nextjs my-app"


def test_synthesize_install_command_git_clone(scraper):
    t = {
        "slug": "/templates/next.js/chatbot",
        "github_url": "https://github.com/vercel/chatbot",
        "frameworks": "ai",
    }
    assert scraper._synthesize_install_command(t) == "git clone https://github.com/vercel/chatbot"
