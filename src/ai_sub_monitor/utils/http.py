from __future__ import annotations

import httpx

DEFAULT_TIMEOUT = httpx.Timeout(20.0)


def get_client() -> httpx.Client:
  return httpx.Client(timeout=DEFAULT_TIMEOUT, follow_redirects=True)
