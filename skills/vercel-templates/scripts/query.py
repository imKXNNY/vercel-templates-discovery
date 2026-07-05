#!/usr/bin/env python3
"""Small helper script for the Hermes vercel-templates skill.

Reads a JSON request from stdin and writes a JSON response to stdout.
Request shape: {"action": "search", "query": "...", "limit": 5}
                {"action": "get", "slug": "/templates/next.js/chatbot"}
                {"action": "categories"}
"""

from __future__ import annotations

import json
import sys

from vercel_templates.scraper import VercelTemplateScraper


def main() -> int:
    request = json.load(sys.stdin)
    action = request.get("action")
    scraper = VercelTemplateScraper()

    if action == "search":
        results = scraper.search(request.get("query", ""), limit=request.get("limit", 10))
        json.dump({"results": results}, sys.stdout, indent=2, ensure_ascii=False)
    elif action == "get":
        result = scraper.get(request.get("slug", ""))
        json.dump({"result": result}, sys.stdout, indent=2, ensure_ascii=False)
    elif action == "categories":
        templates = scraper.all_templates()
        categories: set[str] = set()
        for t in templates:
            for fw in t.get("frameworks", "").split(", "):
                if fw:
                    categories.add(fw)
            for uc in t.get("use_cases", "").split(", "):
                if uc:
                    categories.add(uc)
        json.dump({"categories": sorted(categories)}, sys.stdout, indent=2, ensure_ascii=False)
    else:
        json.dump({"error": f"Unknown action: {action}"}, sys.stdout, indent=2, ensure_ascii=False)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
