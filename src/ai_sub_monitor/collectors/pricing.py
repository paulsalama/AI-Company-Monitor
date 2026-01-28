from __future__ import annotations

import datetime as dt
import hashlib
from pathlib import Path
from typing import Any, Dict, List

from bs4 import BeautifulSoup
from rich.console import Console
from sqlalchemy import select

from ..config import ensure_data_dirs
from ..db import PricingSnapshot, session_scope
from ..utils.http import fetch_with_retries, get_client

console = Console()


def _safe_slug(url: str) -> str:
    return url.replace("https://", "").replace("http://", "").replace("/", "_")


def _extract_structured_pricing(company_id: str, html: str) -> Dict[str, Any] | None:
    """
    Lightweight extractor: grabs obvious $price amounts and maps to known tiers.
    This is heuristic but gives us structured values for workbook updates.
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    amounts = []
    for m in re.finditer(r"\$(\d{1,4})", text):
        try:
            amounts.append(int(m.group(1)))
        except ValueError:
            continue
    amounts = sorted(set(amounts))

    pricing: List[Dict[str, Any]] = []
    if company_id == "anthropic":
        mapping = {20: "pro", 100: "max_5x", 200: "max_20x"}
        for amt in amounts:
            if amt in mapping:
                pricing.append({"tier": mapping[amt], "price_monthly": amt})
    elif company_id == "openai":
        mapping = {20: "plus", 200: "pro"}
        for amt in amounts:
            if amt in mapping:
                pricing.append({"tier": mapping[amt], "price_monthly": amt})

    if not pricing:
        return None

    title = soup.title.string if soup.title else None
    data = {"pricing": pricing}
    if title:
        data["title"] = title
    return data


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run(sources_config: Dict[str, Any]):
    ensure_data_dirs()
    now = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    snapshot_dir = Path("data/snapshots")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    client = get_client()

    for company_id, info in sources_config.get("companies", {}).items():
        pricing_urls = info.get("pricing_urls", [])
        for url in pricing_urls:
            console.print(f"[cyan]Fetching pricing page for {company_id}: {url}[/cyan]")
            try:
                resp = fetch_with_retries(client, url)
                resp.raise_for_status()
            except Exception as exc:
                console.print(f"[red]Failed to fetch {url}: {exc}[/red]")
                continue

            html = resp.text
            content_hash = _hash(html)

            with session_scope() as session:
                prev = session.scalar(
                    select(PricingSnapshot)
                    .where(PricingSnapshot.company_id == company_id, PricingSnapshot.url == url)
                    .order_by(PricingSnapshot.captured_at.desc())
                )
                if prev and prev.content_hash == content_hash:
                    console.print("[green]No change detected; skipping snapshot.[/green]")
                    continue

                filename = snapshot_dir / f"{company_id}_pricing_{_safe_slug(url)}_{now}.html"
                filename.write_text(html, encoding="utf-8")

                structured = _extract_structured_pricing(company_id, html)
                snap = PricingSnapshot(
                    company_id=company_id,
                    url=url,
                    content_hash=content_hash,
                    tier_name="unknown",
                    price_monthly=None,
                    price_annual=None,
                    features=structured,
                    rate_limits_stated=None,
                    raw_html=html,
                    is_change=prev is not None,
                )
                session.add(snap)

                # If previous snapshot exists, write a unified diff for manual review
                if prev:
                    import difflib

                    diff_path = snapshot_dir / f"{company_id}_pricing_{_safe_slug(url)}_{now}.diff"
                    diff_text = "\n".join(
                        difflib.unified_diff(
                            (prev.raw_html or "").splitlines(),
                            html.splitlines(),
                            fromfile="prev",
                            tofile="curr",
                        )
                    )
                    diff_path.write_text(diff_text, encoding="utf-8")
                    console.print(f"[green]Saved diff to {diff_path}[/green]")

                console.print(f"[green]Saved snapshot to {filename}[/green]")
