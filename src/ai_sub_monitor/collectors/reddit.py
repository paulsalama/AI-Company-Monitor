from __future__ import annotations

from typing import Any, Dict

from rich.console import Console

console = Console()


def run(sources_config: Dict[str, Any], keywords_config: Dict[str, Any]):
  """
  Placeholder Reddit collector.
  TODO: Implement PRAW-based ingestion using credentials from env:
        REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT.
  """
  subs = []
  for info in sources_config.get("companies", {}).values():
    subs.extend(info.get("subreddits", []))
  subs = sorted(set(subs))
  console.print(
    "[yellow]Reddit collector not yet implemented. "
    f"Would monitor: {', '.join(subs)}.[/yellow]"
  )
