from __future__ import annotations

import httpx

DEFAULT_TIMEOUT = httpx.Timeout(20.0)
DEFAULT_HEADERS = {
    "User-Agent": "ai-sub-monitor/0.1 (+https://github.com/paulsalama/AI-Company-Monitor)",
}


def get_client() -> httpx.Client:
    return httpx.Client(
        timeout=DEFAULT_TIMEOUT,
        follow_redirects=True,
        headers=DEFAULT_HEADERS,
    )
