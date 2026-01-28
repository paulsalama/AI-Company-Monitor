from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import func, select

from ..config import ensure_data_dirs, default_db_path
from ..db import CommunitySignal, DocumentationSnapshot, PricingSnapshot, session_scope

env = Environment(
    loader=FileSystemLoader(Path(__file__).resolve().parent / "templates"),
    autoescape=select_autoescape(enabled_extensions=("md", "j2")),
)


def _week_bounds(target: Optional[dt.date]) -> tuple[dt.date, dt.date]:
    if target is None:
        target = dt.date.today()
    start = target - dt.timedelta(days=target.weekday())  # Monday
    end = start + dt.timedelta(days=6)
    return start, end


def _community_metrics(start_dt: dt.datetime, end_dt: dt.datetime, db_path) -> tuple[Dict[str, int], float | str]:
    volume: Dict[str, int] = {}
    sentiment = "n/a"
    with session_scope(db_path) as session:
        rows = session.execute(
            select(CommunitySignal.source, func.count())
            .where(
                CommunitySignal.captured_at >= start_dt,
                CommunitySignal.captured_at < end_dt + dt.timedelta(days=1),
            )
            .group_by(CommunitySignal.source)
        ).all()
        volume = {src: count for src, count in rows}

        avg = session.scalar(
            select(func.avg(CommunitySignal.sentiment)).where(
                CommunitySignal.captured_at >= start_dt,
                CommunitySignal.captured_at < end_dt + dt.timedelta(days=1),
                CommunitySignal.sentiment.isnot(None),
            )
        )
        if avg is not None:
            sentiment = round(float(avg), 3)
    return volume, sentiment


def _change_counts(start_dt: dt.datetime, end_dt: dt.datetime, db_path) -> tuple[int, int]:
    pricing_changes = 0
    doc_changes = 0
    with session_scope(db_path) as session:
        pricing_changes = session.scalar(
            select(func.count()).where(
                PricingSnapshot.captured_at >= start_dt,
                PricingSnapshot.captured_at < end_dt + dt.timedelta(days=1),
                PricingSnapshot.is_change.is_(True),
            )
        )
        doc_changes = session.scalar(
            select(func.count()).where(
                DocumentationSnapshot.captured_at >= start_dt,
                DocumentationSnapshot.captured_at < end_dt + dt.timedelta(days=1),
                DocumentationSnapshot.is_change.is_(True),
            )
        )
    return int(pricing_changes or 0), int(doc_changes or 0)


def generate_weekly_report(week_start: Optional[dt.date] = None, db_path=None) -> Path:
    ensure_data_dirs()
    start, end = _week_bounds(week_start)
    start_dt = dt.datetime.combine(start, dt.time.min)
    end_dt = dt.datetime.combine(end, dt.time.max)
    template = env.get_template("weekly_report.md.j2")

    volume, sentiment = _community_metrics(start_dt, end_dt, db_path or default_db_path())
    pricing_changes, doc_changes = _change_counts(start_dt, end_dt, db_path or default_db_path())

    context: Dict[str, Any] = {
        "week_start": start.isoformat(),
        "week_end": end.isoformat(),
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "summary": None,
        "pricing_changes": pricing_changes,
        "rate_limit_changes": doc_changes,
        "community_signal_volume": volume if volume else {},
        "sentiment_trend": sentiment,
        "key_events": [],
    }

    content = template.render(**context)
    reports_dir = Path("data/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    outfile = reports_dir / f"weekly_{start.isoformat()}.md"
    outfile.write_text(content, encoding="utf-8")
    return outfile
