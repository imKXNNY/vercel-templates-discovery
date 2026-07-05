import re
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

from .config import BASE_URL, DEFAULT_CATEGORIES, cache_db_path, user_agent


class VercelTemplateScraper:
    def __init__(self, delay: float = 0.5, max_workers: int = 8):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.delay = delay
        self.max_workers = max_workers
        self.db_path = cache_db_path()
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                framework TEXT,
                title TEXT,
                description TEXT,
                github_url TEXT,
                owner TEXT,
                repository TEXT,
                use_cases TEXT,
                frameworks TEXT,
                css TEXT,
                databases TEXT,
                authentication TEXT,
                cms TEXT,
                experimentation TEXT,
                readme_text TEXT,
                install_command TEXT,
                detail_url TEXT,
                indexed_at INTEGER
            )
            """
        )
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(
                title, description, readme_text, tags
            )
            """
        )
        conn.commit()
        conn.close()

    def reset_db(self) -> None:
        """Drop and recreate tables. Used by index before a full rebuild."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DROP TABLE IF EXISTS search")
        conn.execute("DROP TABLE IF EXISTS templates")
        conn.commit()
        conn.close()
        self._init_db()

    def _get(self, url: str, retries: int = 3) -> requests.Response:
        last_exc: Optional[Exception] = None
        for attempt in range(retries):
            try:
                resp = self.session.get(url, timeout=30)
                if resp.status_code == 200:
                    return resp
                if resp.status_code in (429, 503):
                    time.sleep(2 ** attempt)
                    continue
                resp.raise_for_status()
            except Exception as exc:
                last_exc = exc
                time.sleep(1.5 ** attempt)
        raise last_exc or RuntimeError(f"Failed to fetch {url}")

    def discover_templates(self) -> dict[str, dict[str, Any]]:
        templates: dict[str, dict[str, Any]] = {}
        for category in DEFAULT_CATEGORIES:
            url = f"{BASE_URL}/templates/{category}"
            try:
                resp = self._get(url)
                html = resp.text
                cards = re.findall(
                    r'data-template-card-wrapper[^>]*href="(/templates/[^"]+)".*?<h3[^>]*>([^<]+)</h3>.*?line-clamp-2[^>]*>([^<]+)',
                    html,
                    re.DOTALL,
                )
                for href, title, desc in cards:
                    slug = href.strip()
                    if slug not in templates:
                        templates[slug] = {
                            "slug": slug,
                            "framework": category,
                            "title": _unescape(title.strip()),
                            "description": _unescape(desc.strip()),
                            "detail_url": f"{BASE_URL}{slug}",
                        }
                time.sleep(self.delay)
            except Exception as exc:
                print(f"Warning: failed to discover {category}: {exc}")
        return templates

    def enrich_template(self, slug: str) -> dict[str, Any]:
        url = f"{BASE_URL}{slug}"
        resp = self._get(url)
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else None

        desc_tag = soup.find("p", class_=re.compile(r"text-sm.*text-gray-900"))
        description = desc_tag.get_text(strip=True) if desc_tag else None

        # Fallback: parse the Next.js RSC flight payload embedded in scripts
        scripts = "\n".join(
            tag.string for tag in soup.find_all("script") if tag.string
        )

        github_url = _extract_json_string(scripts, "githubUrl")
        owner = None
        repository = None
        if github_url:
            m = re.search(r"github\.com/([^/]+)/([^/]+)(?:/tree/.+)?", github_url)
            if m:
                owner = m.group(1)
                repository = m.group(2)

        use_cases = _extract_sidebar_values(scripts, "Use Cases")
        frameworks = _extract_sidebar_values(scripts, "Framework")
        css = _extract_sidebar_values(scripts, "CSS")
        databases = _extract_sidebar_values(scripts, "Database")
        auth = _extract_sidebar_values(scripts, "Authentication")
        cms = _extract_sidebar_values(scripts, "CMS")
        experimentation = _extract_sidebar_values(scripts, "Experimentation")

        readme_text = _extract_readme_text(scripts)
        install_command = _extract_install_command(readme_text or "", scripts)

        return {
            "slug": slug,
            "title": title or "",
            "description": description or "",
            "github_url": github_url or "",
            "owner": owner or "",
            "repository": repository or "",
            "use_cases": ", ".join(use_cases),
            "frameworks": ", ".join(frameworks),
            "css": ", ".join(css),
            "databases": ", ".join(databases),
            "authentication": ", ".join(auth),
            "cms": ", ".join(cms),
            "experimentation": ", ".join(experimentation),
            "readme_text": readme_text or "",
            "install_command": install_command or "",
            "detail_url": url,
            "indexed_at": int(time.time()),
        }

    def index(self, concurrency: Optional[int] = None) -> int:
        self.reset_db()
        templates = self.discover_templates()
        if not templates:
            return 0

        workers = concurrency or self.max_workers
        enriched: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self.enrich_template, slug): slug
                for slug in templates
            }
            for future in as_completed(futures):
                slug = futures[future]
                try:
                    data = future.result()
                    # Preserve the category/framework from discovery if enrich didn't set it
                    if not data.get("frameworks") and templates[slug].get("framework"):
                        data["frameworks"] = templates[slug]["framework"]
                    if not data.get("install_command"):
                        data["install_command"] = self._synthesize_install_command(data)
                    enriched.append(data)
                except Exception as exc:
                    print(f"Warning: failed to enrich {slug}: {exc}")

        self._save_templates(enriched)
        return len(enriched)

    def _save_templates(self, templates: list[dict[str, Any]]) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM templates")
        conn.execute("DELETE FROM search")
        for t in templates:
            cur = conn.execute(
                """
                INSERT OR REPLACE INTO templates
                (slug, framework, title, description, github_url, owner, repository,
                 use_cases, frameworks, css, databases, authentication, cms, experimentation,
                 readme_text, install_command, detail_url, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    t.get("slug"),
                    t.get("frameworks", ""),
                    t.get("title", ""),
                    t.get("description", ""),
                    t.get("github_url", ""),
                    t.get("owner", ""),
                    t.get("repository", ""),
                    t.get("use_cases", ""),
                    t.get("frameworks", ""),
                    t.get("css", ""),
                    t.get("databases", ""),
                    t.get("authentication", ""),
                    t.get("cms", ""),
                    t.get("experimentation", ""),
                    t.get("readme_text", ""),
                    t.get("install_command", ""),
                    t.get("detail_url", ""),
                    t.get("indexed_at", 0),
                ),
            )
            rowid = cur.lastrowid
            tags = ", ".join(
                filter(
                    None,
                    [
                        t.get("use_cases", ""),
                        t.get("frameworks", ""),
                        t.get("css", ""),
                        t.get("databases", ""),
                        t.get("authentication", ""),
                        t.get("cms", ""),
                    ],
                )
            )
            conn.execute(
                "INSERT OR REPLACE INTO search (rowid, title, description, readme_text, tags) VALUES (?, ?, ?, ?, ?)",
                (
                    rowid,
                    t.get("title", ""),
                    t.get("description", ""),
                    t.get("readme_text", ""),
                    tags,
                ),
            )
        conn.commit()
        conn.close()

    def _synthesize_install_command(self, t: dict[str, Any]) -> str:
        """Best-effort install command when none was extracted from the README."""
        slug = t.get("slug", "")
        github = t.get("github_url", "")
        if github:
            # If it's a clear Next.js example path, use create-next-app
            m = re.search(r"/examples/([^/]+)$", github)
            if m and "next" in t.get("frameworks", "").lower():
                example = m.group(1)
                return f"npx create-next-app --example {example} my-app"
            # Generic git clone fallback
            return f"git clone {github}"
        # Last resort: derive from slug
        parts = slug.strip("/").split("/")
        if len(parts) >= 2 and "next" in parts[0].lower():
            example = parts[-1]
            return f"npx create-next-app --example {example} my-app"
        return ""

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT t.* FROM templates t
            JOIN search s ON s.rowid = t.id
            WHERE search MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (query, limit),
        )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get(self, slug: str) -> Optional[dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM templates WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def all_templates(self, limit: Optional[int] = None) -> list[dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        sql = "SELECT * FROM templates ORDER BY title"
        params: tuple = ()
        if limit:
            sql += " LIMIT ?"
            params = (limit,)
        cursor = conn.execute(sql, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows


def _unescape(text: str) -> str:
    import html

    return html.unescape(text)


def _extract_json_string(text: str, key: str) -> Optional[str]:
    # The Next.js flight payload escapes quotes as \" in the inline script.
    # Match both escaped and unescaped forms.
    pattern = rf'\\"{re.escape(key)}\\":\s*\\"([^\\"]+)\\"'
    match = re.search(pattern, text)
    if match:
        return _unescape(match.group(1))
    # Fallback: unescaped JSON
    pattern = rf'"{re.escape(key)}":\s*"([^"]+)"'
    match = re.search(pattern, text)
    return match.group(1) if match else None


def _extract_sidebar_values(text: str, label: str) -> list[str]:
    values = []
    # Match the escaped label in the flight payload
    for m in re.finditer(rf'\\"children\\":\\"{re.escape(label)}\\"', text):
        window = text[m.end() : m.end() + 900]
        # Find the next clickable link values
        vals = re.findall(r'\\"children\\":\\"([^\\"]{1,60})\\"', window)
        for v in vals:
            v = _unescape(v)
            if v == label or v in {"GitHub", "Owner", "Repository", "Deploy", "Stack"}:
                continue
            values.append(v)
            if len(values) >= 6:
                break
    return values


def _extract_readme_text(text: str) -> Optional[str]:
    # The README is rendered as a markdown-like string in the flight payload.
    # Try to find a large escaped block near "readmeText" or markdown headings.
    match = re.search(r'\\"readmeText\\":\\"([^\\"]{200,})\\"', text)
    if match:
        raw = match.group(1)
        return _unescape(raw)
    # Fallback: unescaped JSON
    match = re.search(r'"readmeText":"([^"]{200,})"', text)
    if match:
        return _unescape(match.group(1))
    # Fallback: find a long block of escaped text with markdown indicators
    match = re.search(r'(\\n#[^\\"]{200,})', text)
    if match:
        return _unescape(match.group(1).replace("\\n", "\n"))
    return None


def _extract_install_command(readme_text: str, scripts: str) -> Optional[str]:
    # First, try to find a bash code block in the readme text
    for block in re.findall(r"```(?:bash|sh|shell)?\n?(.*?)```", readme_text, re.DOTALL):
        for line in block.splitlines():
            line = line.strip()
            # Prefer scaffold / clone commands
            if line.startswith(("npx create-", "npx create ", "npm create ", "yarn create ", "git clone ", "bunx create-")):
                return line
        # Accept any install command if no scaffold command found
        for line in block.splitlines():
            line = line.strip()
            if line.startswith(("npx ", "npm ", "yarn ", "pnpm ", "bun ", "bunx ")):
                return line
    # Fallback: search the entire scripts payload for escaped or unescaped commands
    for pattern in [
        r'(?:\\")?npx\s+create-[-\w]+(?:\s+[-\w./=]+)*(?:\\")?',
        r'(?:\\")?git clone\s+\S+(?:\\")?',
        r'(?:\\")?npx\s+[-\w]+(?:\s+[-\w./=]+)*(?:\\")?',
    ]:
        match = re.search(pattern, scripts)
        if match:
            return _unescape(match.group(0).strip().strip('"'))
    return None
