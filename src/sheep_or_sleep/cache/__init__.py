"""Cache package for SheepOrSleep."""

from sheep_or_sleep.cache.client import get_redis_client, close_redis_client
from sheep_or_sleep.cache.service import CacheService

__all__ = ["get_redis_client", "close_redis_client", "CacheService"]
