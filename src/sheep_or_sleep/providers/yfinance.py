"""Development-only Market Data Provider using yfinance.

WARNING: This provider is for local development and non-production testing only.
yfinance relies on undocumented scraping of Yahoo Finance endpoints and does not
provide commercial licenses, service-level agreements, or delivery volume data.
"""

from __future__ import annotations

import asyncio
import datetime
import logging
from typing import Optional
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from sheep_or_sleep.providers.base import persist_bars
from sheep_or_sleep.providers.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from sheep_or_sleep.providers.envelope import BarData, QuoteData, Result

logger = logging.getLogger(__name__)


class YFinanceProvider:
    """Market data provider backed by yfinance for development only."""

    def __init__(
        self,
        timeout_seconds: float = 10.0,
        max_attempts: int = 3,
        circuit_breaker: Optional[CircuitBreaker] = None,
    ):
        self.is_dev_only = True
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts
        self.circuit_breaker = circuit_breaker or CircuitBreaker(
            failure_threshold=5, recovery_timeout_sec=30.0
        )

    def _sync_fetch_history(self, symbol: str, start: datetime.date, end: datetime.date) -> pd.DataFrame:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start.isoformat(), end=end.isoformat(), auto_adjust=False)
        return df

    def _sync_fetch_quote(self, symbol: str) -> dict:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        fast_info = getattr(ticker, "fast_info", None)
        if fast_info:
            price = fast_info.last_price or 0.0
            prev_close = fast_info.previous_close or price
            change = price - prev_close
            change_pct = (change / prev_close * 100.0) if prev_close else 0.0
            return {
                "price": float(price),
                "change": float(change),
                "change_percent": float(change_pct),
            }
        return {"price": 0.0, "change": 0.0, "change_percent": 0.0}

    async def fetch_bars(
        self, symbol: str, start: datetime.date, end: datetime.date
    ) -> Result[list[BarData]]:
        try:
            async with self.circuit_breaker:
                async for attempt in AsyncRetrying(
                    reraise=True,
                    stop=stop_after_attempt(self.max_attempts),
                    wait=wait_exponential_jitter(multiplier=0.5, max=4.0),
                    retry=retry_if_exception_type(Exception),
                ):
                    with attempt:
                        df = await asyncio.wait_for(
                            asyncio.to_thread(self._sync_fetch_history, symbol, start, end),
                            timeout=self.timeout_seconds,
                        )

            if df is None or df.empty:
                return Result(
                    status="unavailable",
                    as_of=datetime.datetime.now(datetime.timezone.utc),
                    data_version=end.isoformat(),
                    value=None,
                    reason=f"No data returned by provider for {symbol}",
                )

            bars: list[BarData] = []
            for dt, row in df.iterrows():
                bar_date = dt.date() if hasattr(dt, "date") else dt
                bars.append(
                    BarData(
                        ts=bar_date,
                        open=float(row.get("Open", 0.0)),
                        high=float(row.get("High", 0.0)),
                        low=float(row.get("Low", 0.0)),
                        close=float(row.get("Close", 0.0)),
                        volume=int(row.get("Volume", 0)),
                        deliv_qty=None,
                        adj_factor=float(row.get("Adj Close", row.get("Close", 1.0))) / float(row.get("Close", 1.0))
                        if row.get("Close", 0)
                        else 1.0,
                    )
                )

            return Result(
                status="ok",
                as_of=datetime.datetime.now(datetime.timezone.utc),
                data_version=end.isoformat(),
                value=bars,
                reason=None,
            )

        except CircuitBreakerOpenError as cbe:
            return Result(
                status="unavailable",
                as_of=datetime.datetime.now(datetime.timezone.utc),
                data_version=end.isoformat(),
                value=None,
                reason=str(cbe),
            )
        except Exception as exc:
            logger.warning("Error fetching bars from yfinance for %s: %s", symbol, exc)
            return Result(
                status="unavailable",
                as_of=datetime.datetime.now(datetime.timezone.utc),
                data_version=end.isoformat(),
                value=None,
                reason=f"Upstream provider error: {type(exc).__name__}",
            )

    async def fetch_quote(self, symbol: str) -> Result[QuoteData]:
        try:
            async with self.circuit_breaker:
                quote_raw = await asyncio.wait_for(
                    asyncio.to_thread(self._sync_fetch_quote, symbol),
                    timeout=self.timeout_seconds,
                )

            now = datetime.datetime.now(datetime.timezone.utc)
            return Result(
                status="ok",
                as_of=now,
                data_version=now.date().isoformat(),
                value=QuoteData(
                    price=quote_raw["price"],
                    change=quote_raw["change"],
                    change_percent=quote_raw["change_percent"],
                    as_of=now,
                ),
                reason=None,
            )
        except CircuitBreakerOpenError as cbe:
            return Result(
                status="unavailable",
                as_of=datetime.datetime.now(datetime.timezone.utc),
                data_version=datetime.date.today().isoformat(),
                value=None,
                reason=str(cbe),
            )
        except Exception as exc:
            logger.warning("Error fetching quote from yfinance for %s: %s", symbol, exc)
            return Result(
                status="unavailable",
                as_of=datetime.datetime.now(datetime.timezone.utc),
                data_version=datetime.date.today().isoformat(),
                value=None,
                reason=f"Upstream provider error: {type(exc).__name__}",
            )

    async def fetch_and_store_bars(
        self,
        session: AsyncSession,
        instrument_id: int,
        symbol: str,
        start: datetime.date,
        end: datetime.date,
    ) -> Result[int]:
        res = await self.fetch_bars(symbol, start, end)
        if res.status != "ok" or not res.value:
            return Result(
                status=res.status,
                as_of=res.as_of,
                data_version=res.data_version,
                value=0,
                reason=res.reason,
            )

        stored = await persist_bars(session, instrument_id, res.value, source="yfinance")
        return Result(
            status="ok",
            as_of=res.as_of,
            data_version=res.data_version,
            value=stored,
            reason=None,
        )
