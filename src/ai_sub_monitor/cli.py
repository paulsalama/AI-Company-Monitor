from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .collectors import docs as docs_collector
from .collectors import github as github_collector
from .collectors import pricing as pricing_collector
from .collectors import reddit as reddit_collector
from .config import default_db_path, ensure_data_dirs, load_sources_and_keywords
from .db import Company, FinancialEvent, init_db, session_scope
from .reporters.weekly import generate_weekly_report

console = Console()


def _seed_companies():
    sources, _ = load_sources_and_keywords()
    companies = sources.get("companies", {})
    with session_scope() as session:
        for cid, info in companies.items():
            if session.get(Company, cid):
                continue
            session.add(Company(id=cid, name=info.get("name", cid.title())))
        session.commit()


@click.group()
@click.version_option(__version__)
@click.option(
    "--db",
    "db_path",
    type=click.Path(path_type=Path),
    default=default_db_path,
    help="Path to SQLite database file.",
)
@click.pass_context
def cli(ctx: click.Context, db_path: Path):
    """AI Subscription Economics Monitor CLI."""
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = db_path


@cli.command()
@click.pass_context
def init(ctx: click.Context):
    """Initialize local folders, database, and seed company metadata."""
    db_path: Path = ctx.obj["db_path"]
    ensure_data_dirs()
    init_db(db_path)
    _seed_companies()

    # copy spreadsheet templates into data/models for safe keeping
    root = Path(__file__).resolve().parents[2]
    src_files = {
        "subscription_economics.xlsx",
        "subscriber_mix_model.xlsx",
    }
    dest_dir = root / "data" / "models"
    dest_dir.mkdir(parents=True, exist_ok=True)
    for filename in src_files:
        src = root / filename
        if src.exists():
            dst = dest_dir / filename
            if not dst.exists():
                shutil.copy(src, dst)
    console.print(f"[green]Initialized database at {db_path}[/green]")
    console.print("[green]Seeded companies from config/sources.yaml[/green]")


@cli.command()
@click.option(
    "--source",
    type=click.Choice(["all", "pricing", "reddit", "github", "docs"], case_sensitive=False),
    default="all",
    help="Collector to run.",
)
@click.pass_context
def collect(ctx: click.Context, source: str):
    """Run one or more data collectors."""
    db_path: Path = ctx.obj["db_path"]
    ensure_data_dirs()
    init_db(db_path)

    sources, keywords = load_sources_and_keywords()
    if source in ("all", "pricing"):
        pricing_collector.run(sources)
    if source in ("all", "reddit"):
        reddit_collector.run(sources, keywords)
    if source in ("all", "github"):
        github_collector.run(sources, keywords)
    if source in ("all", "docs"):
        docs_collector.run(sources)

    console.print("[green]Collect step finished (see logs for details).[/green]")


@cli.command("report")
@click.option("--week", "week_start", type=click.DateTime(formats=["%Y-%m-%d"]), required=False)
@click.option("--latest", is_flag=True, help="Generate for the most recent Monday.")
@click.pass_context
def report_cmd(ctx: click.Context, week_start, latest: bool):
    """Generate a weekly markdown report."""
    db_path: Path = ctx.obj["db_path"]
    ensure_data_dirs()
    init_db(db_path)
    week: Optional[date] = None
    if latest:
        week = date.today()
    elif week_start:
        week = week_start.date()
    path = generate_weekly_report(week_start=week)
    console.print(f"[green]Report generated at {path}[/green]")


@cli.command("add-event")
@click.option("--company", required=True, type=click.Choice(["anthropic", "openai"]))
@click.option("--type", "event_type", required=True)
@click.option("--amount", type=float, required=False)
@click.option("--valuation", type=float, required=False)
@click.option("--date", "event_date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.option("--source", "source_url", type=str, required=False)
@click.option("--notes", type=str, required=False)
@click.pass_context
def add_event(
    ctx: click.Context,
    company: str,
    event_type: str,
    amount: float | None,
    valuation: float | None,
    event_date,
    source_url: str | None,
    notes: str | None,
):
    """Manually add a financial event."""
    db_path: Path = ctx.obj["db_path"]
    ensure_data_dirs()
    init_db(db_path)
    with session_scope(db_path) as session:
        event = FinancialEvent(
            company_id=company,
            event_type=event_type,
            amount=amount,
            valuation=valuation,
            event_date=event_date.date(),
            source_url=source_url,
            notes=notes,
        )
        session.add(event)
    console.print("[green]Financial event added.[/green]")


@cli.command()
@click.pass_context
def sources(ctx: click.Context):
    """List configured sources for quick inspection."""
    sources, _ = load_sources_and_keywords()
    table = Table(title="Configured Sources")
    table.add_column("Company")
    table.add_column("Pricing URLs")
    table.add_column("Docs URLs")
    table.add_column("Repos")
    table.add_column("Subreddits")
    for cid, info in sources.get("companies", {}).items():
        table.add_row(
            cid,
            "\n".join(info.get("pricing_urls", [])),
            "\n".join(info.get("docs_urls", [])),
            "\n".join(info.get("github_repos", [])),
            "\n".join(info.get("subreddits", [])),
        )
    console.print(table)


if __name__ == "__main__":
    cli()
