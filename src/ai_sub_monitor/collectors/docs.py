from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict

import httpx
from rich.console import Console

console = Console()


def _safe_slug(url: str) -> str:
  return url.replace("https://", "").replace("http://", "").replace("/", "_")


def run(sources_config: Dict[str, Any]):
  now = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
  for company_id, info in sources_config.get("companies", {}).items():
    docs_urls = info.get("docs_urls", [])
    for url in docs_urls:
      console.print(f"[cyan]Fetching docs for {company_id}: {url}[/cyan]")
      try:
        resp = httpx.get(url, timeout=20)
        resp.raise_for_status()
      except Exception as exc:
        console.print(f"[red]Failed to fetch {url}: {exc}[/red]")
        continue
      html = resp.text
      path = Path("data/snapshots") / f"{company_id}_docs_{_safe_slug(url)}_{now}.html"
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text(html, encoding="utf-8")
      console.print(f"[green]Saved docs snapshot to {path}[/green]")
