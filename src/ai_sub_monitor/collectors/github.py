from __future__ import annotations

from typing import Any, Dict

from rich.console import Console

console = Console()


def run(sources_config: Dict[str, Any], keywords_config: Dict[str, Any]):
  """
  Placeholder GitHub collector.
  TODO: Implement PyGithub-based issue search using GITHUB_TOKEN env.
  """
  repos = []
  for info in sources_config.get("companies", {}).values():
    repos.extend(info.get("github_repos", []))
  repos = sorted(set(repos))
  console.print(
    "[yellow]GitHub collector not yet implemented. "
    f"Would monitor: {', '.join(repos)}.[/yellow]"
  )
