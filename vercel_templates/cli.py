import json
from pathlib import Path
from typing import Optional

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
):
    """Crawl and index the Vercel Templates catalog."""
    scraper = VercelTemplateScraper(delay=delay, max_workers=concurrency)
    with console.status("[bold green]Discovering templates..."):
        count = scraper.index(concurrency=concurrency)
    console.print(f"[bold green]Indexed {count} templates[/bold green]")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max results"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """Search the indexed templates."""
    scraper = VercelTemplateScraper()
    results = scraper.search(query, limit=limit)
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        raise typer.Exit(0)

    if json_output:
        console.print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    table = Table(title=f'Vercel Templates matching "{query}"')
    table.add_column("Title", style="cyan", no_wrap=False)
    table.add_column("Framework", style="magenta")
    table.add_column("Use Cases", style="green")
    table.add_column("Description", style="white")

    for r in results:
        table.add_row(
            r.get("title", ""),
            r.get("frameworks", ""),
            r.get("use_cases", ""),
            r.get("description", "")[:120] + "...",
        )
    console.print(table)


@app.command()
def show(
    slug: str = typer.Argument(..., help="Template slug, e.g. /templates/next.js/chatbot"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
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
[b]Description:[/b] {t.get('description', '')}
[b]Frameworks:[/b] {t.get('frameworks', '')}
[b]Use Cases:[/b] {t.get('use_cases', '')}
[b]Owner:[/b] {t.get('owner', '')}
[b]Repository:[/b] {t.get('repository', '')}
[b]GitHub URL:[/b] {t.get('github_url', '')}
[b]Install:[/b] {t.get('install_command', '')}
[b]Detail:[/b] {t.get('detail_url', '')}
""".strip()
    console.print(Panel(body, title=title, expand=False))
    if t.get("readme_text"):
        console.print("\n[bold]README excerpt:[/bold]")
        console.print(t.get("readme_text", "")[:1500])


@app.command()
def export(
    output: Path = typer.Option(Path("templates.json"), "--output", "-o", help="JSON output path"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit number of templates"),
):
    """Export the indexed templates to JSON."""
    scraper = VercelTemplateScraper()
    templates = scraper.all_templates(limit=limit)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(templates, f, indent=2, ensure_ascii=False)
    console.print(f"[bold green]Exported {len(templates)} templates to {output}[/bold green]")


@app.command()
def stats():
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


if __name__ == "__main__":
    app()
