"""Tests for MarketDataProvider Protocol, FakeProvider, CircuitBreaker, and Bar Persistence.

Phase 1 Step 3: Provider Layer
"""

import datetime
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


@pytest.mark.asyncio
async def test_fake_provider_ok_and_failure_modes():
    """Verify FakeProvider returns proper Result envelopes in ok and error states."""
    from sheep_or_sleep.providers.fake import FakeProvider
    from sheep_or_sleep.providers.envelope import BarData, QuoteData

    # 1. OK mode
    provider = FakeProvider(status_override=None)
    res_bars = await provider.fetch_bars("RELIANCE.NS", datetime.date(2024, 1, 1), datetime.date(2024, 1, 10))
    assert res_bars.status == "ok"
    assert res_bars.value is not None
    assert len(res_bars.value) == 10
    assert isinstance(res_bars.value[0], BarData)
    assert res_bars.value[0].close > 0

    res_quote = await provider.fetch_quote("RELIANCE.NS")
    assert res_quote.status == "ok"
    assert res_quote.value is not None
    assert isinstance(res_quote.value, QuoteData)
    assert res_quote.value.price > 0

    # 2. Simulated failure mode
    failing_provider = FakeProvider(status_override="unavailable", failure_reason="Upstream HTTP 503")
    res_failed = await failing_provider.fetch_bars("RELIANCE.NS", datetime.date(2024, 1, 1), datetime.date(2024, 1, 10))
    assert res_failed.status == "unavailable"
    assert res_failed.value is None
    assert res_failed.reason == "Upstream HTTP 503"


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    """Verify circuit breaker trips on consecutive errors and resets on recovery."""
    from sheep_or_sleep.providers.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

    cb = CircuitBreaker(failure_threshold=3, recovery_timeout_sec=0.2)
    assert cb.state == "CLOSED"

    # Register 3 failures to trip breaker
    for _ in range(3):
        with pytest.raises(ValueError):
            async with cb:
                raise ValueError("Simulated network outage")

    assert cb.state == "OPEN"

    # In OPEN state, calls must immediately fail without executing inner block
    called = False
    with pytest.raises(CircuitBreakerOpenError):
        async with cb:
            called = True
    assert not called

    # Wait for recovery timeout
    import asyncio
    await asyncio.sleep(0.25)
    assert cb.state == "HALF_OPEN"

    # A successful call resets circuit to CLOSED
    async with cb:
        pass
    assert cb.state == "CLOSED"


@pytest.mark.asyncio
async def test_fetch_and_store_bars_in_database():
    """Verify provider bars are ingested and persisted idempotently into bars_1d."""
    from sheep_or_sleep.db.base import Base
    from sheep_or_sleep.db.models import Bar1D
    from sheep_or_sleep.providers.fake import FakeProvider

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    provider = FakeProvider()
    async with session_factory() as session:
        # Initial ingestion of 10 bars
        res = await provider.fetch_and_store_bars(
            session=session,
            instrument_id=42,
            symbol="TCS.NS",
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
        )
        assert res.status == "ok"
        assert res.value == 10

        # Query back from DB
        stored_bars = (await session.execute(select(Bar1D).where(Bar1D.instrument_id == 42))).scalars().all()
        assert len(stored_bars) == 10

        # Ingest again with same dates (should be idempotent upsert / no duplicate key error)
        res_repeat = await provider.fetch_and_store_bars(
            session=session,
            instrument_id=42,
            symbol="TCS.NS",
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 1, 10),
        )
        assert res_repeat.status == "ok"
        stored_bars_after = (await session.execute(select(Bar1D).where(Bar1D.instrument_id == 42))).scalars().all()
        assert len(stored_bars_after) == 10

    await engine.dispose()


def test_yfinance_provider_dev_only_metadata():
    """Verify YFinanceProvider explicitly flags itself as dev-only."""
    from sheep_or_sleep.providers.yfinance import YFinanceProvider

    provider = YFinanceProvider()
    assert provider.is_dev_only is True
    assert "development only" in provider.__doc__.lower()


@pytest.mark.asyncio
async def test_yfinance_provider_error_handling_and_circuit_breaker(monkeypatch):
    """Verify YFinanceProvider handles exceptions gracefully and trips circuit breaker."""
    from sheep_or_sleep.providers.yfinance import YFinanceProvider
    from sheep_or_sleep.providers.circuit_breaker import CircuitBreaker

    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_sec=10.0)
    provider = YFinanceProvider(max_attempts=1, circuit_breaker=cb)

    def mock_fail(*args, **kwargs):
        raise ConnectionError("Mock network failure")

    monkeypatch.setattr(provider, "_sync_fetch_history", mock_fail)

    # First failure
    res1 = await provider.fetch_bars("INFY.NS", datetime.date(2024, 1, 1), datetime.date(2024, 1, 5))
    assert res1.status == "unavailable"
    assert "ConnectionError" in (res1.reason or "")

    # Second failure trips circuit breaker
    res2 = await provider.fetch_bars("INFY.NS", datetime.date(2024, 1, 1), datetime.date(2024, 1, 5))
    assert res2.status == "unavailable"

    # Circuit breaker is now OPEN
    assert cb.state == "OPEN"
    res3 = await provider.fetch_bars("INFY.NS", datetime.date(2024, 1, 1), datetime.date(2024, 1, 5))
    assert res3.status == "unavailable"
    assert "Circuit breaker is OPEN" in (res3.reason or "")

