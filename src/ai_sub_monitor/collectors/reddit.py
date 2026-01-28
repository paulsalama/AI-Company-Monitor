from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import praw
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
    # de-duplicate, lower
    return sorted(set(kw.lower() for kw in kws))


def _map_sub_to_company(sources_config: Dict[str, Any]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for cid, info in sources_config.get("companies", {}).items():
        for sub in info.get("subreddits", []):
            mapping[sub.lower()] = cid
    return mapping


def run(sources_config: Dict[str, Any], keywords_config: Dict[str, Any], lookback_hours: int = 24):
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "ai-sub-monitor/0.1")
    if not (client_id and client_secret):
        console.print(
            "[yellow]Skipping Reddit collector: missing REDDIT_CLIENT_ID/SECRET env vars.[/yellow]"
        )
        return

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        check_for_async=False,
    )

    keywords = _collect_keywords(keywords_config)
    sub_map = _map_sub_to_company(sources_config)
    subs = sorted(sub_map.keys())
    if not subs:
        console.print("[yellow]No subreddits configured; skipping Reddit collector.[/yellow]")
        return

    since_ts = time.time() - (lookback_hours * 3600)
    new_signals = 0

    with session_scope() as session:
        for sub_name in subs:
            subreddit = reddit.subreddit(sub_name)
            console.print(f"[cyan]Scanning r/{sub_name}[/cyan]")
            for submission in subreddit.new(limit=100):
                if submission.created_utc < since_ts:
                    continue
                text = f"{submission.title}\n\n{submission.selftext or ''}"
                hits = _keyword_hits(text, keywords)
                if not hits:
                    continue
                source_id = submission.id
                exists = session.scalar(
                    select(CommunitySignal).where(
                        CommunitySignal.source == "reddit", CommunitySignal.source_id == source_id
                    )
                )
                if exists:
                    continue
                company_id = sub_map.get(sub_name.lower())
                if not company_id:
                    # Skip subs that aren't mapped to a company
                    continue
                sentiment = sentiment_score(text)
                signal = CommunitySignal(
                    company_id=company_id,
                    source="reddit",
                    source_id=source_id,
                    captured_at=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                    content=text[:10000],  # keep payload bounded
                    url=submission.url,
                    sentiment=sentiment,
                    keywords_matched=hits,
                    score=submission.score,
                    comment_count=submission.num_comments,
                )
                session.add(signal)
                new_signals += 1

    console.print(f"[green]Reddit collector complete. Added {new_signals} signals.[/green]")
