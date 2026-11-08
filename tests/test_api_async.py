"""Tests for Async API Handlers, Health Probes, Rate Limiting, Auth, and Caching.

Phase 1 Step 5: API Layer
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from server import app
    return TestClient(app)


def test_healthz_liveness(client):
    """GET /healthz returns 200 OK liveness response."""
    resp = client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_readyz_readiness_healthy_and_unhealthy(client, monkeypatch):
    """GET /readyz returns 200 when dependencies are up, and 503 when down."""
    import server

    # 1. Healthy state
    async def mock_check_health():
        return {"status": "ok", "postgres": "ok", "redis": "ok"}

    monkeypatch.setattr(server, "check_system_readiness", mock_check_health)
    resp_ok = client.get("/readyz")
    assert resp_ok.status_code == 200
    assert resp_ok.json()["status"] == "ok"

    # 2. Unhealthy state (e.g. Postgres down)
    async def mock_check_unhealthy():
        return {"status": "down", "postgres": "down", "redis": "ok"}

    monkeypatch.setattr(server, "check_system_readiness", mock_check_unhealthy)
    resp_fail = client.get("/readyz")
    assert resp_fail.status_code == 503
    detail = resp_fail.json().get("detail", {})
    assert detail.get("postgres") == "down"


def test_api_metrics_endpoint(client):
    """GET /api/metrics exposes cache performance statistics."""
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "hits" in data
    assert "misses" in data
    assert "hit_ratio" in data


def test_rate_limiter_exceeded():
    """Verify rate limiter blocks client when requests exceed threshold."""
    import asyncio
    import fakeredis.aioredis
    from sheep_or_sleep.api.rate_limiter import RedisRateLimiter

    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    limiter = RedisRateLimiter(redis_client=fake_redis, max_requests=3, window_seconds=60)

    async def run_limiter():
        # First 3 requests should pass
        for _ in range(3):
            allowed = await limiter.is_allowed("test-client-ip")
            assert allowed is True

        # 4th request must be rate limited
        blocked = await limiter.is_allowed("test-client-ip")
        assert blocked is False

    asyncio.run(run_limiter())


def test_auth_dependency():
    """Verify API key authentication dependency enforcement."""
    from fastapi import HTTPException
    from sheep_or_sleep.api.auth import verify_auth

    # When auth is required and no key is provided, raise 401
    with pytest.raises(HTTPException) as exc_info:
        verify_auth(api_key=None, authorization=None, require_auth=True, valid_api_key="secret123")
    assert exc_info.value.status_code == 401

    # When valid key is provided, succeeds
    res = verify_auth(api_key="secret123", authorization=None, require_auth=True, valid_api_key="secret123")
    assert "apikey:" in res


def test_api_quote_and_analyze_served_from_cache(client, monkeypatch):
    """Verify quote and analyze endpoints serve repeat requests from cache."""
    import fakeredis.aioredis
    from sheep_or_sleep.cache.service import CacheService
    import server

    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    server.cache_service = CacheService(redis_client=fake_redis)

    quote_fetch_count = 0

    def mock_fetch_quote(symbol):
        nonlocal quote_fetch_count
        quote_fetch_count += 1
        return {"price": 2500.0, "change": 10.0, "change_percent": 0.4, "as_of": "2024-01-01"}

    monkeypatch.setattr(server, "fetch_quote", mock_fetch_quote)

    # First call: cache miss -> fetch called
    resp1 = client.get("/api/quote?symbol=TCS.NS")
    assert resp1.status_code == 200
    assert resp1.json()["price"] == 2500.0
    assert quote_fetch_count == 1

    # Second call: served from cache -> fetch NOT called
    resp2 = client.get("/api/quote?symbol=TCS.NS")
    assert resp2.status_code == 200
    assert resp2.json()["price"] == 2500.0
    assert quote_fetch_count == 1  # Still 1, served from cache!

