from pathlib import Path
from typing import Optional

DEFAULT_CATEGORIES = [
    "ai",
    "authentication",
    "backend",
    "blog",
    "cms",
    "cron",
    "documentation",
    "ecommerce",
    "edge-config",
    "edge-middleware",
    "marketing-sites",
    "microfrontends",
    "monorepos",
    "multi-tenant-apps",
    "portfolio",
    "realtime-apps",
    "saas",
    "security",
    "starter",
    "vercel-firewall",
    "virtual-event",
    "web3",
    # Framework categories
    "next.js",
    "nuxt",
    "svelte",
    "astro",
    "hono",
    "express",
    "flask",
    "remix",
    "vue",
    "angular",
    "react",
    "solid",
    "qwik",
    "other",
]

FRAMEWORK_CATEGORIES = {
    "next.js", "nuxt", "svelte", "astro", "hono", "express", "flask",
    "remix", "vue", "angular", "react", "solid", "qwik", "other",
}


def cache_db_path() -> Path:
    home = Path.home()
    cache_dir = home / ".vercel_templates"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "templates.db"


def user_agent() -> str:
    return (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
