from __future__ import annotations

import datetime as dt
import hashlib
from pathlib import Path
from typing import Any, Dict

from rich.console import Console
from sqlalchemy import select

from ..db import DocumentationSnapshot, session_scope
from ..utils.http import get_client

console = Console()


def _safe_slug(url: str) -> str:
    return url.replace("https://", "").replace("http://", "").replace("/", "_")


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run(sources_config: Dict[str, Any]):
    now = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    client = get_client()
    for company_id, info in sources_config.get("companies", {}).items():
        docs_urls = info.get("docs_urls", [])
        for url in docs_urls:
            console.print(f"[cyan]Fetching docs for {company_id}: {url}[/cyan]")
            try:
                resp = client.get(url)
                resp.raise_for_status()
            except Exception as exc:
                console.print(f"[red]Failed to fetch {url}: {exc}[/red]")
                continue
            html = resp.text
            content_hash = _hash(html)
            with session_scope() as session:
                prev = session.scalar(
                    select(DocumentationSnapshot)
                    .where(DocumentationSnapshot.company_id == company_id, DocumentationSnapshot.url == url)
                    .order_by(DocumentationSnapshot.captured_at.desc())
                )
                if prev and prev.content_hash == content_hash:
                    console.print("[green]No change detected; skipping snapshot.[/green]")
                    continue
                path = Path("data/snapshots") / f"{company_id}_docs_{_safe_slug(url)}_{now}.html"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(html, encoding="utf-8")

                snap = DocumentationSnapshot(
                    company_id=company_id,
                    url=url,
                    content_hash=content_hash,
                    raw_html=html,
                    is_change=prev is not None,
                )
                session.add(snap)
                console.print(f"[green]Saved docs snapshot to {path}[/green]")
