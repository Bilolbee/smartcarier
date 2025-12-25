"""
=============================================================================
REDIS CLIENT (SYNC)
=============================================================================

Small, safe Redis client wrapper used by:
- token blacklist (logout)
- rate limiting (production)
- oauth state storage (CSRF protection)

Design goals:
- Works without Redis (falls back gracefully)
- Single shared connection (lazy init)
- No async/await dependency (can be used inside sync dependencies)
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_redis() -> Optional["Redis"]:
    """
    Get a shared Redis client, or None if disabled/unavailable.

    We intentionally keep this sync so it can be called from sync code paths
    (e.g. token verification dependencies).
    """
    redis_url = getattr(settings, "REDIS_URL", "") or ""
    enabled = bool(getattr(settings, "REDIS_ENABLED", False))

    if not enabled or not redis_url:
        return None

    try:
        import redis  # type: ignore

        client = redis.Redis.from_url(
            redis_url,
            decode_responses=True,  # store strings
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        # quick health check
        client.ping()
        logger.info("Redis connected")
        return client
    except Exception as e:
        logger.warning(f"Redis unavailable, falling back to in-memory: {e}")
        return None


