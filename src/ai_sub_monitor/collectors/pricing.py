from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict

import httpx
from bs4 import BeautifulSoup
from rich.console import Console

from ..config import ensure_data_dirs
from ..db import PricingSnapshot, session_scope

console = Console()


def _safe_slug(url: str) -> str:
  return url.replace("https://", "").replace("http://", "").replace("/", "_")


def _extract_structured_pricing(html: str) -> Dict[str, Any] | None:
  """
  Minimal placeholder extractor. In v1 we simply return None and rely on raw_html snapshots.
  Later we can parse tiers and prices explicitly.
  """
  soup = BeautifulSoup(html, "html.parser")
  title = soup.title.string if soup.title else None
  return {"title": title} if title else None


def run(sources_config: Dict[str, Any]):
  ensure_data_dirs()
  now = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
  for company_id, info in sources_config.get("companies", {}).items():
    pricing_urls = info.get("pricing_urls", [])
    for url in pricing_urls:
      console.print(f"[cyan]Fetching pricing page for {company_id}: {url}[/cyan]")
      try:
        resp = httpx.get(url, timeout=20)
        resp.raise_for_status()
      except Exception as exc:
        console.print(f"[red]Failed to fetch {url}: {exc}[/red]")
        continue

      html = resp.text
      snapshot_dir = Path("data/snapshots")
      snapshot_dir.mkdir(parents=True, exist_ok=True)
      filename = snapshot_dir / f"{company_id}_pricing_{_safe_slug(url)}_{now}.html"
      filename.write_text(html, encoding="utf-8")

      structured = _extract_structured_pricing(html)
      with session_scope() as session:
        snap = PricingSnapshot(
          company_id=company_id,
          tier_name="unknown",
          price_monthly=None,
          price_annual=None,
          features=None,
          rate_limits_stated=None,
          raw_html=filename.read_text(encoding="utf-8"),
        )
        if structured:
          snap.features = structured
        session.add(snap)
      console.print(f"[green]Saved snapshot to {filename}[/green]")
