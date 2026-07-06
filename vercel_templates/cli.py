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
def export(
    output: str = typer.Option("templates.json", "--output", "-o", help="JSON output path"),
    limit: int | None = typer.Option(None, "--limit", "-n", help="Limit number of templates"),
) -> None:
    """Export the indexed templates to JSON."""
    scraper = VercelTemplateScraper()
    templates = scraper.all_templates(limit=limit)
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
