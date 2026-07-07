from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException

from .scraper import VercelTemplateScraper

app = FastAPI(title="Vercel Templates Discovery API", version="0.2.0")
_scraper: VercelTemplateScraper | None = None


def get_scraper(embedding_model: Any = None) -> VercelTemplateScraper:
    global _scraper  # noqa: PLW0603
    if _scraper is None:
        _scraper = VercelTemplateScraper(embedding_model=embedding_model)
    return _scraper


def set_scraper(scraper: VercelTemplateScraper | None) -> None:
    global _scraper  # noqa: PLW0603
    _scraper = scraper


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/templates")
def list_templates(
    scraper: Annotated[VercelTemplateScraper, Depends(get_scraper)],
    q: str = "",
    limit: int = 10,
) -> list[dict[str, Any]]:
    if q:
        return scraper.search(q, limit=limit)
    return scraper.all_templates(limit=limit)


@app.get("/templates/semantic")
def search_semantic(
    q: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    try:
        from .embeddings import get_model

        scraper = get_scraper(embedding_model=get_model())
        return scraper.semantic_search(q, limit=limit)
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="Semantic search not installed. Add the semantic extra.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/templates/{slug:path}")
def get_template(
    slug: str,
    scraper: Annotated[VercelTemplateScraper, Depends(get_scraper)],
) -> dict[str, Any]:
    full_slug = f"/templates/{slug}"
    result = scraper.get(full_slug)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Template {full_slug} not found")
    return result


@app.get("/categories")
def list_categories(
    scraper: Annotated[VercelTemplateScraper, Depends(get_scraper)],
) -> list[str]:
    templates = scraper.all_templates()
    categories: set[str] = set()
    for t in templates:
        for fw in t.get("frameworks", "").split(", "):
            if fw:
                categories.add(fw)
        for uc in t.get("use_cases", "").split(", "):
            if uc:
                categories.add(uc)
    return sorted(categories)


@app.get("/templates/recent")
def list_recent(
    scraper: Annotated[VercelTemplateScraper, Depends(get_scraper)],
    hours: int = 24,
    limit: int = 10,
) -> list[dict[str, Any]]:
    return scraper.recently_added(hours=hours, limit=limit)


@app.get("/templates/trending")
def list_trending(
    scraper: Annotated[VercelTemplateScraper, Depends(get_scraper)],
    hours: int = 168,
    limit: int = 10,
    by_category: bool = False,
) -> dict[str, Any]:
    return scraper.trending(hours=hours, limit=limit, by_category=by_category)
