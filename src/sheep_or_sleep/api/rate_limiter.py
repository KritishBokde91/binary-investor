"""Redis-backed rate limiter per IP address and API key."""

from __future__ import annotations

import os
from typing import Optional
from fastapi import HTTPException, Request, status
import redis.asyncio as aioredis

from sheep_or_sleep.cache.client import get_redis_client


class RedisRateLimiter:
    """Sliding/fixed window rate limiter backed by Redis."""

    def __init__(
        self,
        redis_client: Optional[aioredis.Redis] = None,
        max_requests: int = 60,
        window_seconds: int = 60,
    ):
        self._redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    @property
    def redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = get_redis_client()
        return self._redis

    async def is_allowed(self, identifier: str) -> bool:
        """Check if request for identifier is within allowable rate limits."""
        key = f"rate_limit:{identifier}"
        try:
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, self.window_seconds)
            results = await pipe.execute()
            count = results[0]
            return count <= self.max_requests
        except Exception:
            # If Redis is temporarily unavailable, fail open to avoid rejecting valid traffic
            return True


_global_limiter: Optional[RedisRateLimiter] = None


def get_rate_limiter() -> RedisRateLimiter:
    global _global_limiter
    if _global_limiter is None:
        max_req = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
        _global_limiter = RedisRateLimiter(max_requests=max_req, window_seconds=60)
    return _global_limiter


async def check_rate_limit(request: Request):
    """FastAPI dependency enforcing rate limits per client IP / API key."""
    # Check if rate limiting is enabled
    enabled = os.getenv("ENABLE_RATE_LIMIT", "false").lower() in ("true", "1")
    if not enabled:
        return

    client_ip = request.client.host if request.client else "unknown"
    forwarded = request.headers.get("X-Forwarded-For")
    client_id = forwarded.split(",")[0].strip() if forwarded else client_ip

    limiter = get_rate_limiter()
    allowed = await limiter.is_allowed(client_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please retry in a few moments.",
        )
