"""Tests for Redis Cache with Single-Flight Locking and Stale-While-Revalidate.

Phase 1 Step 4: Cache Layer
"""

import asyncio
import pytest
import fakeredis.aioredis


@pytest.fixture
def fake_redis():
    """In-memory async Redis instance for isolated tests."""
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.mark.asyncio
async def test_cache_hit_and_miss_metrics(fake_redis):
    """Verify cache records hits, misses, and hit ratio accurately."""
    from sheep_or_sleep.cache.service import CacheService

    cache = CacheService(redis_client=fake_redis)

    call_count = 0

    async def expensive_calc():
        nonlocal call_count
        call_count += 1
        return {"result": 42}

    # 1. First call: Cache miss, loader executed
    val1 = await cache.get_or_compute("calc:test", expensive_calc, ttl_sec=60)
    assert val1 == {"result": 42}
    assert call_count == 1

    metrics = await cache.get_metrics()
    assert metrics["hits"] == 0
    assert metrics["misses"] == 1
    assert metrics["hit_ratio"] == 0.0

    # 2. Second call: Cache hit, loader NOT executed
    val2 = await cache.get_or_compute("calc:test", expensive_calc, ttl_sec=60)
    assert val2 == {"result": 42}
    assert call_count == 1

    metrics2 = await cache.get_metrics()
    assert metrics2["hits"] == 1
    assert metrics2["misses"] == 1
    assert metrics2["hit_ratio"] == 0.5


@pytest.mark.asyncio
async def test_single_flight_stampede_protection(fake_redis):
    """Verify concurrent requests for the same key trigger the loader only once."""
    from sheep_or_sleep.cache.service import CacheService

    cache = CacheService(redis_client=fake_redis)
    call_count = 0

    async def slow_loader():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.05)
        return {"symbol": "RELIANCE.NS", "score": 99}

    # Launch 10 simultaneous concurrent requests for the exact same key
    tasks = [
        cache.get_or_compute("panic:RELIANCE.NS", slow_loader, ttl_sec=60)
        for _ in range(10)
    ]
    results = await asyncio.gather(*tasks)

    # Every concurrent request received the correct result
    for res in results:
        assert res == {"symbol": "RELIANCE.NS", "score": 99}

    # Dogpiling / stampede prevented: loader ran exactly once
    assert call_count == 1

    metrics = await cache.get_metrics()
    # 1 miss (first request) + 9 hits/waits
    assert metrics["misses"] == 1
    assert metrics["hits"] == 9
    assert metrics["stampedes_prevented"] >= 1


@pytest.mark.asyncio
async def test_stale_while_revalidate(fake_redis):
    """Verify stale data is returned immediately while refreshing in background."""
    from sheep_or_sleep.cache.service import CacheService

    cache = CacheService(redis_client=fake_redis)
    counter = 0

    async def counter_loader():
        nonlocal counter
        counter += 1
        return {"version": counter}

    # 1. Populate cache with 1s fresh TTL and 5s stale window
    val1 = await cache.get_or_compute("stale:key", counter_loader, ttl_sec=1, stale_ttl_sec=5)
    assert val1 == {"version": 1}
    assert counter == 1

    # Wait for fresh TTL to expire (now in stale window)
    await asyncio.sleep(1.1)

    # 2. Request during stale window: returns stale data immediately, refreshes in background
    val2 = await cache.get_or_compute("stale:key", counter_loader, ttl_sec=1, stale_ttl_sec=5)
    assert val2 == {"version": 1}  # Stale hit

    # Wait for background task to complete
    await asyncio.sleep(0.1)
    assert counter == 2

    # 3. Subsequent request gets the newly revalidated value
    val3 = await cache.get_or_compute("stale:key", counter_loader, ttl_sec=1, stale_ttl_sec=5)
    assert val3 == {"version": 2}


@pytest.mark.asyncio
async def test_cache_direct_get_set_and_reset_metrics(fake_redis):
    """Verify raw get/set and resetting metrics."""
    from sheep_or_sleep.cache.service import CacheService

    cache = CacheService(redis_client=fake_redis)
    await cache.set("direct:key", {"val": "hello"}, ttl_sec=60)

    val = await cache.get("direct:key")
    assert val == {"val": "hello"}

    # Non-existent key returns None
    assert await cache.get("nonexistent") is None

    # Reset metrics
    await cache.get_or_compute("dummy", lambda: asyncio.sleep(0, result=1), ttl_sec=60)
    metrics_before = await cache.get_metrics()
    assert metrics_before["misses"] == 1

    await cache.reset_metrics()
    metrics_after = await cache.get_metrics()
    assert metrics_after["hits"] == 0
    assert metrics_after["misses"] == 0
    assert metrics_after["hit_ratio"] == 0.0

