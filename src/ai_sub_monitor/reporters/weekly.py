from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..config import ensure_data_dirs

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


def generate_weekly_report(week_start: Optional[dt.date] = None) -> Path:
  ensure_data_dirs()
  start, end = _week_bounds(week_start)
  template = env.get_template("weekly_report.md.j2")

  # Placeholder metrics until collectors populate the database
  context: Dict[str, Any] = {
    "week_start": start.isoformat(),
    "week_end": end.isoformat(),
    "generated_at": dt.datetime.utcnow().isoformat() + "Z",
    "summary": None,
    "pricing_changes": 0,
    "rate_limit_changes": 0,
    "community_signal_volume": "{}",
    "sentiment_trend": "n/a",
    "key_events": [],
  }

  content = template.render(**context)
  reports_dir = Path("data/reports")
  reports_dir.mkdir(parents=True, exist_ok=True)
  outfile = reports_dir / f"weekly_{start.isoformat()}.md"
  outfile.write_text(content, encoding="utf-8")
  return outfile
