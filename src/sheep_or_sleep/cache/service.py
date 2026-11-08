"""Redis cache service with single-flight locking (SET NX PX) and stale-while-revalidate."""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from typing import Any, Callable, Coroutine, Optional
import redis.asyncio as aioredis

from sheep_or_sleep.cache.client import get_redis_client

logger = logging.getLogger(__name__)

RELEASE_LOCK_LUA = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""


def _sanitize_for_json(val: Any) -> Any:
    """Recursively convert NumPy/Pandas scalars, dates, arrays, etc., to standard JSON serializable primitives."""
    if hasattr(val, "tolist"):
        try:
            return _sanitize_for_json(val.tolist())
        except Exception:
            pass
    if hasattr(val, "item"):
        try:
            return _sanitize_for_json(val.item())
        except Exception:
            pass
    if isinstance(val, (int, str, bool)):
        return val
    if isinstance(val, float):
        import math
        if math.isnan(val) or math.isinf(val):
            return 0.0
        return val
    if isinstance(val, dict):
        return {k: _sanitize_for_json(v) for k, v in val.items()}
    if isinstance(val, (list, tuple, set)):
        return [_sanitize_for_json(v) for v in val]
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return val


class CacheService:
    """Async Redis caching service with dogpile stampede protection and stale-while-revalidate."""

    def __init__(
        self,
        redis_client: Optional[aioredis.Redis] = None,
        metrics_key: str = "cache:metrics:sheep_or_sleep",
    ):
        self._redis = redis_client or get_redis_client()
        self.metrics_key = metrics_key

        self._hits = 0
        self._misses = 0
        self._stale_hits = 0
        self._stampedes_prevented = 0

    async def get_metrics(self) -> dict[str, Any]:
        """Return cache performance metrics including hit ratio."""
        total = self._hits + self._misses
        ratio = round(self._hits / total, 4) if total > 0 else 0.0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "stale_hits": self._stale_hits,
            "stampedes_prevented": self._stampedes_prevented,
            "hit_ratio": ratio,
        }

    async def reset_metrics(self):
        self._hits = 0
        self._misses = 0
        self._stale_hits = 0
        self._stampedes_prevented = 0

    async def _acquire_lock(self, lock_key: str, token: str, timeout_ms: int = 5000) -> bool:
        """Acquire distributed lock via SET key token NX PX timeout_ms."""
        res = await self._redis.set(lock_key, token, px=timeout_ms, nx=True)
        return bool(res)

    async def _release_lock(self, lock_key: str, token: str):
        """Safely release distributed lock using Lua script with atomic fallback."""
        try:
            await self._redis.eval(RELEASE_LOCK_LUA, 1, lock_key, token)
        except Exception:
            try:
                curr = await self._redis.get(lock_key)
                if isinstance(curr, bytes):
                    curr = curr.decode("utf-8")
                if curr == token:
                    await self._redis.delete(lock_key)
            except Exception as e:
                logger.warning("Error releasing cache lock %s: %s", lock_key, e)

    async def get(self, key: str) -> Optional[Any]:
        """Fetch raw cached payload."""
        try:
            data_str = await self._redis.get(key)
            if not data_str:
                return None
            payload = json.loads(data_str)
            return payload.get("value")
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl_sec: int, stale_ttl_sec: int = 0):
        """Store value with fresh TTL and optional stale window."""
        now = time.time()
        fresh_until = now + ttl_sec
        stale_until = now + ttl_sec + stale_ttl_sec
        total_ttl = ttl_sec + stale_ttl_sec

        payload = {
            "value": _sanitize_for_json(value),
            "fresh_until": fresh_until,
            "stale_until": stale_until,
        }
        try:
            await self._redis.set(key, json.dumps(payload), ex=total_ttl)
        except Exception as e:
            logger.warning("Redis set failed for %s: %s", key, e)

    async def get_or_compute(
        self,
        key: str,
        loader: Callable[[], Coroutine[Any, Any, Any]],
        ttl_sec: int = 300,
        stale_ttl_sec: int = 0,
        lock_timeout_ms: int = 5000,
    ) -> Any:
        """Fetch from cache, coordinate single-flight lock on misses, or stale-while-revalidate."""
        now = time.time()
        try:
            cached_raw = await self._redis.get(key)
        except Exception as e:
            logger.warning("Redis unavailable during get, bypassing cache for %s: %s", key, e)
            self._misses += 1
            return await loader()

        if cached_raw:
            try:
                payload = json.loads(cached_raw)
                val = payload["value"]
                fresh_until = payload.get("fresh_until", 0)
                stale_until = payload.get("stale_until", 0)

                if now < fresh_until:
                    # Pure cache hit
                    self._hits += 1
                    return val

                if fresh_until <= now < stale_until:
                    # Stale-While-Revalidate window
                    self._stale_hits += 1
                    # Fire background revalidation using single-flight lock
                    asyncio.create_task(
                        self._revalidate(key, loader, ttl_sec, stale_ttl_sec, lock_timeout_ms)
                    )
                    return val
            except Exception as e:
                logger.warning("Cache payload deserialize error for %s: %s", key, e)

        # Cache MISS
        lock_key = f"lock:{key}"
        token = str(uuid.uuid4())

        # Attempt to acquire single-flight lock
        acquired = await self._acquire_lock(lock_key, token, timeout_ms=lock_timeout_ms)
        if acquired:
            self._misses += 1
            try:
                # Double-check cache in case another worker just filled it
                recheck = await self._redis.get(key)
                if recheck:
                    try:
                        p = json.loads(recheck)
                        self._hits += 1
                        self._misses -= 1
                        return p["value"]
                    except Exception:
                        pass

                # Compute value via loader
                result = await loader()
                await self.set(key, result, ttl_sec, stale_ttl_sec)
                return result
            finally:
                await self._release_lock(lock_key, token)
        else:
            # Stampede prevented: another coroutine holds the computation lock
            self._stampedes_prevented += 1
            start_wait = time.monotonic()
            wait_limit = lock_timeout_ms / 1000.0

            while time.monotonic() - start_wait < wait_limit:
                await asyncio.sleep(0.01)
                data = await self._redis.get(key)
                if data:
                    try:
                        self._hits += 1
                        p = json.loads(data)
                        return p["value"]
                    except Exception:
                        break

            # Fallback if wait timed out
            self._misses += 1
            fallback_res = await loader()
            await self.set(key, fallback_res, ttl_sec, stale_ttl_sec)
            return fallback_res

    async def _revalidate(
        self,
        key: str,
        loader: Callable[[], Coroutine[Any, Any, Any]],
        ttl_sec: int,
        stale_ttl_sec: int,
        lock_timeout_ms: int,
    ):
        """Background coroutine to revalidate stale cache entry."""
        lock_key = f"lock:{key}"
        token = str(uuid.uuid4())
        acquired = await self._acquire_lock(lock_key, token, timeout_ms=lock_timeout_ms)
        if not acquired:
            return

        try:
            new_value = await loader()
            await self.set(key, new_value, ttl_sec, stale_ttl_sec)
        except Exception as e:
            logger.warning("Background cache revalidation failed for %s: %s", key, e)
        finally:
            await self._release_lock(lock_key, token)
