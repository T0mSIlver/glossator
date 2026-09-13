"""The z.ai token window, polled before a batch of judgements (D-028)."""

from __future__ import annotations

import asyncio
import os

import httpx
import structlog

logger = structlog.get_logger(__name__)


ZAI_QUOTA_URL = "https://api.z.ai/api/monitor/usage/quota/limit"
QUOTA_CEILING_PERCENT = 80
"""D-028: pause before a batch when the five-hour token window is this full."""


async def zai_headroom(client: httpx.AsyncClient | None = None) -> int | None:
    """Percent of the five-hour z.ai token window already used (D-028).

    None when the endpoint cannot be read: a quota check that fails is a reason
    to say so, not a reason to refuse to judge.
    """
    key = os.environ.get("ZAI_API_KEY")
    if not key:
        return None
    owned = client is None
    http = client or httpx.AsyncClient(timeout=20.0)
    try:
        response = await http.get(ZAI_QUOTA_URL, headers={"Authorization": f"Bearer {key}"})
        response.raise_for_status()
        limits = response.json()["data"]["limits"]
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
        logger.warning("z.ai quota unreadable", error=str(error))
        return None
    finally:
        if owned:
            await http.aclose()
    for limit in limits:
        if limit.get("type") == "TOKENS_LIMIT":
            return int(limit.get("percentage", 0))
    return None


async def wait_for_quota(ceiling: int = QUOTA_CEILING_PERCENT) -> int | None:
    """Poll the quota before a batch and pause while it is above the ceiling."""
    used = await zai_headroom()
    while used is not None and used >= ceiling:
        logger.warning("z.ai token window above the ceiling, pausing", used=used, ceiling=ceiling)
        await asyncio.sleep(300)
        used = await zai_headroom()
    return used
