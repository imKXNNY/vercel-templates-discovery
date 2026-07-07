import datetime
import json

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .scraper import VercelTemplateScraper

app = typer.Typer(help="Discover and search Vercel Templates")
console = Console()


@app.command()
def index(
    concurrency: int = typer.Option(8, "--concurrency", "-c", help="Max parallel detail fetches"),
    delay: float = typer.Option(0.5, "--delay", "-d", help="Seconds between category requests"),
    reset: bool = typer.Option(False, "--reset", help="Drop existing index before re-indexing"),
) -> None:
    """Crawl and index the Vercel Templates catalog."""
    scraper = VercelTemplateScraper(delay=delay, max_workers=concurrency)
    if reset:
        scraper.reset_db()
        console.print("[yellow]Existing index dropped.[/yellow]")
    with console.status("[bold green]Discovering templates..."):
        count = scraper.index(concurrency=concurrency)
    console.print(f"[bold green]Indexed {count} templates[/bold green]")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max results"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
    semantic: bool = typer.Option(False, "--semantic", help="Use semantic search"),
) -> None:
    """Search the indexed templates."""
    if semantic:
        _semantic_search(query, limit=limit, json_output=json_output)
        return
    scraper = VercelTemplateScraper()
    results = scraper.search(query, limit=limit)
    _render_results(
        results, query, json_output, title_template='Vercel Templates matching "{query}"'
    )


def _semantic_search(query: str, limit: int, json_output: bool) -> None:
    try:
        from .embeddings import get_model
    except ImportError as exc:
        console.print(
            "[red]Semantic search requires the semantic extra. "
            "Install with: pip install 'vercel-templates-discovery[semantic]'[/red]"
        )
        raise typer.Exit(1) from exc

    scraper = VercelTemplateScraper(embedding_model=get_model())
    try:
        results = scraper.semantic_search(query, limit=limit)
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    _render_results(
        results,
        query,
        json_output,
        title_template='Semantic matches for "{query}"',
        show_distance=True,
    )


def _render_results(
    results: list[dict[str, object]],
    query: str,
    json_output: bool,
    title_template: str,
    show_distance: bool = False,
) -> None:
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        raise typer.Exit(0)

    if json_output:
        console.print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    table = Table(title=title_template.format(query=query))
    table.add_column("Title", style="cyan", no_wrap=False)
    table.add_column("Framework", style="magenta")
    table.add_column("Use Cases", style="green")
    if show_distance:
        table.add_column("Distance", style="yellow", justify="right")
    table.add_column("Description", style="white")

    for r in results:
        desc = r.get("description", "")
        snippet = desc[:120]
        ellipsis = "..." if len(desc) > 120 else ""
        row = [
            r.get("title", ""),
            r.get("frameworks", ""),
            r.get("use_cases", ""),
        ]
        if show_distance:
            distance = r.get("distance")
            row.append(f"{distance:.4f}" if isinstance(distance, (int, float)) else "")
        row.append(f"{snippet}{ellipsis}")
        table.add_row(*row)
    console.print(table)


@app.command()
def semantic(
    query: str = typer.Argument(..., help="Semantic search query"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max results"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
) -> None:
    """Search indexed templates by semantic similarity."""
    _semantic_search(query, limit=limit, json_output=json_output)


@app.command()
def show(
    slug: str = typer.Argument(..., help="Template slug, e.g. /templates/next.js/chatbot"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
) -> None:
    """Show full details for a template."""
    scraper = VercelTemplateScraper()
    t = scraper.get(slug)
    if not t:
        console.print(f"[red]Template {slug} not found. Run `vercel-templates index` first.[/red]")
        raise typer.Exit(1)

    if json_output:
        console.print(json.dumps(t, indent=2, ensure_ascii=False))
        return

    title = t.get("title", slug)
    body = f"""
[b]Description:[/b] {t.get("description", "")}
[b]Frameworks:[/b] {t.get("frameworks", "")}
[b]Use Cases:[/b] {t.get("use_cases", "")}
[b]Owner:[/b] {t.get("owner", "")}
[b]Repository:[/b] {t.get("repository", "")}
[b]GitHub URL:[/b] {t.get("github_url", "")}
[b]Install:[/b] {t.get("install_command", "")}
[b]Detail:[/b] {t.get("detail_url", "")}
""".strip()
    console.print(Panel(body, title=title, expand=False))
    if t.get("readme_text"):
        console.print("\n[bold]README excerpt:[/bold]")
        console.print(t.get("readme_text", "")[:1500])


@app.command()
def diff(
    slug_a: str = typer.Argument(..., help="First template slug"),
    slug_b: str = typer.Argument(..., help="Second template slug"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
    fields: str = typer.Option(
        "title,description,frameworks,use_cases,github_url,install_command,readme_text",
        "--fields",
        help="Comma-separated fields to compare",
    ),
) -> None:
    """Compare two indexed templates side by side."""
    scraper = VercelTemplateScraper()
    a = scraper.get(slug_a)
    b = scraper.get(slug_b)
    if not a or not b:
        missing = slug_a if not a else slug_b
        console.print(
            f"[red]Template {missing} not found. Run `vercel-templates index` first.[/red]"
        )
        raise typer.Exit(1)

    selected_fields = [f.strip() for f in fields.split(",") if f.strip()]
    comparison: dict[str, dict[str, object]] = {}
    for field in selected_fields:
        comparison[field] = {
            "a": a.get(field, ""),
            "b": b.get(field, ""),
            "same": a.get(field, "") == b.get(field, ""),
        }

    if json_output:
        console.print(json.dumps(comparison, indent=2, ensure_ascii=False))
        return

    table = Table(title=f"Diff: {slug_a} vs {slug_b}")
    table.add_column("Field", style="cyan")
    table.add_column(slug_a, style="magenta")
    table.add_column(slug_b, style="green")
    table.add_column("Match", style="yellow", justify="center")

    for field, values in comparison.items():
        a_val = str(values["a"])[:200]
        b_val = str(values["b"])[:200]
        match = "✓" if values["same"] else "✗"
        table.add_row(field, a_val, b_val, match)

    console.print(table)


@app.command()
def export(
    output: str = typer.Option("templates.json", "--output", "-o", help="JSON output path"),
    limit: int | None = typer.Option(None, "--limit", "-n", help="Limit number of templates"),
    include_readmes: bool = typer.Option(
        False,
        "--include-readmes",
        help="Include full README text in export (may raise copyright concerns)",
    ),
) -> None:
    """Export the indexed templates to JSON."""
    scraper = VercelTemplateScraper()
    templates = scraper.all_templates(limit=limit)
    if not include_readmes:
        templates = [{k: v for k, v in t.items() if k != "readme_text"} for t in templates]
    with open(output, "w", encoding="utf-8") as f:
        json.dump(templates, f, indent=2, ensure_ascii=False)
    console.print(f"[bold green]Exported {len(templates)} templates to {output}[/bold green]")


@app.command()
def stats() -> None:
    """Show index statistics."""
    scraper = VercelTemplateScraper()
    templates = scraper.all_templates()
    console.print(f"[bold green]{len(templates)} templates indexed[/bold green]")
    frameworks: dict[str, int] = {}
    for t in templates:
        for fw in t.get("frameworks", "").split(", "):
            if fw:
                frameworks[fw] = frameworks.get(fw, 0) + 1
    table = Table(title="Frameworks")
    table.add_column("Framework", style="cyan")
    table.add_column("Count", style="magenta")
    for fw, count in sorted(frameworks.items(), key=lambda x: x[1], reverse=True):
        table.add_row(fw, str(count))
    console.print(table)


@app.command()
def recent(
    hours: int = typer.Option(24, "--hours", "-h", help="How many hours back to look"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max results"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
) -> None:
    """Show templates added to the index recently."""
    scraper = VercelTemplateScraper()
    results = scraper.recently_added(hours=hours, limit=limit)
    if json_output:
        console.print(json.dumps(results, indent=2, ensure_ascii=False))
        return
    if not results:
        console.print(f"[yellow]No templates indexed in the last {hours} hours.[/yellow]")
        return
    table = Table(title=f"Templates indexed in the last {hours} hours")
    table.add_column("Title", style="cyan")
    table.add_column("Slug", style="magenta")
    table.add_column("Framework", style="green")
    table.add_column("Indexed At", style="yellow")
    for t in results:
        indexed = t.get("indexed_at", 0)
        dt = datetime.datetime.fromtimestamp(indexed).strftime("%Y-%m-%d %H:%M") if indexed else ""
        table.add_row(t.get("title", ""), t.get("slug", ""), t.get("frameworks", ""), dt)
    console.print(table)


@app.command()
def trending(
    hours: int = typer.Option(168, "--hours", "-h", help="How many hours back to look"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max results per category"),
    by_category: bool = typer.Option(False, "--by-category", help="Group results by category"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
) -> None:
    """Show trending (recently added) templates."""
    scraper = VercelTemplateScraper()
    data = scraper.trending(hours=hours, limit=limit, by_category=by_category)
    if json_output:
        console.print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    if by_category:
        grouped = data.get("grouped", {})
        if not grouped:
            console.print(f"[yellow]No trending templates in the last {hours} hours.[/yellow]")
            return
        for category, items in sorted(grouped.items()):
            table = Table(title=f"Trending in {category} ({len(items)})")
            table.add_column("Title", style="cyan")
            table.add_column("Slug", style="magenta")
            table.add_column("Indexed At", style="yellow")
            for t in items:
                indexed = t.get("indexed_at", 0)
                dt = (
                    datetime.datetime.fromtimestamp(indexed).strftime("%Y-%m-%d %H:%M")
                    if indexed
                    else ""
                )
                table.add_row(t.get("title", ""), t.get("slug", ""), dt)
            console.print(table)
    else:
        templates = data.get("templates", [])
        if not templates:
            console.print(f"[yellow]No trending templates in the last {hours} hours.[/yellow]")
            return
        table = Table(
            title=f"Trending templates in the last {hours} hours ({data.get('total', 0)} total)"
        )
        table.add_column("Title", style="cyan")
        table.add_column("Slug", style="magenta")
        table.add_column("Framework", style="green")
        table.add_column("Indexed At", style="yellow")
        for t in templates:
            indexed = t.get("indexed_at", 0)
            dt = (
                datetime.datetime.fromtimestamp(indexed).strftime("%Y-%m-%d %H:%M")
                if indexed
                else ""
            )
            table.add_row(t.get("title", ""), t.get("slug", ""), t.get("frameworks", ""), dt)
        console.print(table)


@app.command()
def recommend(
    stack: str = typer.Argument(
        ..., help="Comma-separated desired stack/features, e.g. 'next.js,prisma,auth'"
    ),
    limit: int = typer.Option(10, "--limit", "-n", help="Max results"),
    require_all_frameworks: bool = typer.Option(
        False, "--require-all-frameworks", help="Require all framework terms to match"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
) -> None:
    """Recommend templates based on a target stack or feature set."""
    scraper = VercelTemplateScraper()
    stack_list = [s.strip() for s in stack.split(",") if s.strip()]
    if not stack_list:
        console.print("[red]Provide at least one stack term.[/red]")
        raise typer.Exit(1)
    results = scraper.recommend(
        stack_list, limit=limit, require_all_frameworks=require_all_frameworks
    )
    if json_output:
        console.print(json.dumps(results, indent=2, ensure_ascii=False))
        return
    if not results:
        console.print("[yellow]No recommendations found.[/yellow]")
        return
    table = Table(title=f"Recommended templates for: {stack}")
    table.add_column("Title", style="cyan")
    table.add_column("Slug", style="magenta")
    table.add_column("Framework", style="green")
    table.add_column("Score", style="yellow", justify="right")
    table.add_column("Matches", style="white")
    for t in results:
        table.add_row(
            t.get("title", ""),
            t.get("slug", ""),
            t.get("frameworks", ""),
            str(t.get("recommend_score", "")),
            ", ".join(t.get("recommend_matches", [])),
        )
    console.print(table)


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Bind host"),
    port: int = typer.Option(8000, "--port", "-p", help="Bind port"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload (dev)"),
) -> None:
    """Start the REST API server."""
    try:
        import uvicorn
    except ImportError as exc:
        console.print(
            "[red]uvicorn is required for the server. "
            "Install it with: pip install 'vercel-templates-discovery[server]'[/red]"
        )
        raise typer.Exit(1) from exc

    console.print(f"[bold green]Starting server at http://{host}:{port}[/bold green]")
    uvicorn.run("vercel_templates.server:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
