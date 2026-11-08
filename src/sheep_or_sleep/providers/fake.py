"""Fake / Test implementation of MarketDataProvider for fast, deterministic unit & integration tests."""

from __future__ import annotations

import datetime
from typing import Literal, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from sheep_or_sleep.providers.base import persist_bars
from sheep_or_sleep.providers.envelope import BarData, QuoteData, Result


class FakeProvider:
    """Deterministic in-memory market data provider for unit and integration testing."""

    def __init__(
        self,
        status_override: Optional[Literal["ok", "stale", "degraded", "unavailable"]] = None,
        failure_reason: Optional[str] = None,
        base_price: float = 100.0,
    ):
        self.status_override = status_override
        self.failure_reason = failure_reason
        self.base_price = base_price
        self.is_dev_only = False

    async def fetch_bars(
        self, symbol: str, start: datetime.date, end: datetime.date
    ) -> Result[list[BarData]]:
        if self.status_override and self.status_override != "ok":
            return Result(
                status=self.status_override,
                as_of=datetime.datetime.now(datetime.timezone.utc),
                data_version=end.isoformat(),
                value=None,
                reason=self.failure_reason or f"Simulated {self.status_override} state",
            )

        # Generate deterministic daily bars
        bars: list[BarData] = []
        curr = start
        current_price = self.base_price
        step = 0
        while curr <= end:
            # Deterministic variation
            daily_factor = 1.0 + (0.005 * ((step % 5) - 2))
            open_p = current_price
            close_p = current_price * daily_factor
            high_p = max(open_p, close_p) * 1.01
            low_p = min(open_p, close_p) * 0.99
            vol = 100000 + (step * 5000)

            bars.append(
                BarData(
                    ts=curr,
                    open=round(open_p, 2),
                    high=round(high_p, 2),
                    low=round(low_p, 2),
                    close=round(close_p, 2),
                    volume=vol,
                    deliv_qty=int(vol * 0.4),
                    adj_factor=1.0,
                )
            )
            current_price = close_p
            curr += datetime.timedelta(days=1)
            step += 1

        return Result(
            status="ok",
            as_of=datetime.datetime.now(datetime.timezone.utc),
            data_version=end.isoformat(),
            value=bars,
            reason=None,
        )

    async def fetch_quote(self, symbol: str) -> Result[QuoteData]:
        if self.status_override and self.status_override != "ok":
            return Result(
                status=self.status_override,
                as_of=datetime.datetime.now(datetime.timezone.utc),
                data_version=datetime.date.today().isoformat(),
                value=None,
                reason=self.failure_reason or f"Simulated {self.status_override} state",
            )

        now = datetime.datetime.now(datetime.timezone.utc)
        return Result(
            status="ok",
            as_of=now,
            data_version=now.date().isoformat(),
            value=QuoteData(
                price=round(self.base_price, 2),
                change=1.50,
                change_percent=1.50,
                as_of=now,
            ),
            reason=None,
        )

    async def fetch_and_store_bars(
        self,
        session: AsyncSession,
        instrument_id: int,
        symbol: str,
        start: datetime.date,
        end: datetime.date,
    ) -> Result[int]:
        bars_res = await self.fetch_bars(symbol, start, end)
        if bars_res.status != "ok" or not bars_res.value:
            return Result(
                status=bars_res.status,
                as_of=bars_res.as_of,
                data_version=bars_res.data_version,
                value=0,
                reason=bars_res.reason,
            )

        count = await persist_bars(session, instrument_id, bars_res.value, source="fake_provider")
        return Result(
            status="ok",
            as_of=bars_res.as_of,
            data_version=bars_res.data_version,
            value=count,
            reason=None,
        )
