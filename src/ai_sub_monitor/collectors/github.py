from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from github import Github
from rich.console import Console
from sqlalchemy import select

from ..analyzers.sentiment import score as sentiment_score
from ..db import CommunitySignal, session_scope

console = Console()


def _keyword_hits(text: str, keywords: List[str]) -> List[str]:
    text_l = text.lower()
    return [kw for kw in keywords if kw in text_l]


def _collect_keywords(keywords_config: Dict[str, Any]) -> List[str]:
    kws: List[str] = []
    for val in keywords_config.values():
        if isinstance(val, list):
            kws.extend(val)
    return sorted(set(kw.lower() for kw in kws))


def _map_repo_to_company(sources_config: Dict[str, Any]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for cid, info in sources_config.get("companies", {}).items():
        for repo in info.get("github_repos", []):
            mapping[repo.lower()] = cid
    return mapping


def run(sources_config: Dict[str, Any], keywords_config: Dict[str, Any], lookback_hours: int = 24):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        console.print("[yellow]Skipping GitHub collector: missing GITHUB_TOKEN env var.[/yellow]")
        return

    gh = Github(token, per_page=50)
    keywords = _collect_keywords(keywords_config)
    repo_map = _map_repo_to_company(sources_config)
    repos = sorted(repo_map.keys())
    if not repos:
        console.print("[yellow]No GitHub repos configured; skipping GitHub collector.[/yellow]")
        return

    since_dt = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    new_signals = 0

    with session_scope() as session:
        for repo_full in repos:
            try:
                repo = gh.get_repo(repo_full)
            except Exception as exc:
                console.print(f"[red]Failed to access {repo_full}: {exc}[/red]")
                continue
            console.print(f"[cyan]Scanning issues in {repo_full}[/cyan]")
            try:
                issues = repo.get_issues(state="all", since=since_dt)
            except Exception as exc:
                console.print(f"[red]Issue fetch failed for {repo_full}: {exc}[/red]")
                continue

            for issue in issues:
                if issue.pull_request is not None:
                    continue  # skip PRs
                text = f"{issue.title}\n\n{issue.body or ''}"
                hits = _keyword_hits(text, keywords)
                if not hits:
                    continue
                source_id = f"{repo_full}#{issue.number}"
                exists = session.scalar(
                    select(CommunitySignal).where(
                        CommunitySignal.source == "github", CommunitySignal.source_id == source_id
                    )
                )
                if exists:
                    continue
                company_id = repo_map.get(repo_full.lower())
                if not company_id:
                    continue
                sentiment = sentiment_score(text)
                signal = CommunitySignal(
                    company_id=company_id,
                    source="github",
                    source_id=source_id,
                    captured_at=issue.updated_at.replace(tzinfo=timezone.utc),
                    content=text[:10000],
                    url=issue.html_url,
                    sentiment=sentiment,
                    keywords_matched=hits,
                    score=issue.reactions.total_count if hasattr(issue, "reactions") else None,
                    comment_count=issue.comments,
                )
                session.add(signal)
                new_signals += 1

    console.print(f"[green]GitHub collector complete. Added {new_signals} signals.[/green]")
