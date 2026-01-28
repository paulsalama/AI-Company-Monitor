from __future__ import annotations

import httpx

DEFAULT_TIMEOUT = httpx.Timeout(20.0)
DEFAULT_HEADERS = {
    "User-Agent": "ai-sub-monitor/0.1 (+https://github.com/paulsalama/AI-Company-Monitor)",
    "Accept-Language": "en-US,en;q=0.9",
}


def get_client() -> httpx.Client:
    return httpx.Client(
        timeout=DEFAULT_TIMEOUT,
        follow_redirects=True,
        headers=DEFAULT_HEADERS,
    )


def fetch_with_retries(
    client: httpx.Client,
    url: str,
    max_attempts: int = 3,
    backoff_seconds: float = 2.0,
) -> httpx.Response | None:
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        try:
            return client.get(url)
        except Exception:
            if attempt >= max_attempts:
                raise
        if backoff_seconds:
            import time

            time.sleep(backoff_seconds * attempt)
    return None
