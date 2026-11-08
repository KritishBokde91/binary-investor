"""Redis async client connection manager."""

import os
from typing import Optional
import redis.asyncio as aioredis

DEFAULT_REDIS_URL = "redis://localhost:6379/0"

_global_redis_client: Optional[aioredis.Redis] = None


def get_redis_url() -> str:
    return os.getenv("REDIS_URL", DEFAULT_REDIS_URL)


def get_redis_client() -> aioredis.Redis:
    global _global_redis_client
    if _global_redis_client is None:
        _global_redis_client = aioredis.from_url(
            get_redis_url(),
            encoding="utf-8",
            decode_responses=True,
        )
    return _global_redis_client


async def close_redis_client():
    global _global_redis_client
    if _global_redis_client is not None:
        await _global_redis_client.close()
        _global_redis_client = None
