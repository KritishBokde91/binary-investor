"""Market Data Provider Protocol and persistence helpers."""

from __future__ import annotations

import datetime
from typing import Protocol, runtime_checkable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from sheep_or_sleep.db.models import Bar1D
from sheep_or_sleep.providers.envelope import BarData, QuoteData, Result


@runtime_checkable
class MarketDataProvider(Protocol):
    """Protocol defining the interface for market data sources."""

    async def fetch_bars(
        self, symbol: str, start: datetime.date, end: datetime.date
    ) -> Result[list[BarData]]:
        """Fetch historical daily bars for a symbol."""
        ...

    async def fetch_quote(self, symbol: str) -> Result[QuoteData]:
        """Fetch the latest quote for a symbol."""
        ...

    async def fetch_and_store_bars(
        self,
        session: AsyncSession,
        instrument_id: int,
        symbol: str,
        start: datetime.date,
        end: datetime.date,
    ) -> Result[int]:
        """Fetch bars and persist them into the bars_1d table."""
        ...


async def persist_bars(
    session: AsyncSession,
    instrument_id: int,
    bars: list[BarData],
    source: str,
) -> int:
    """Idempotently insert or update daily bars in bars_1d."""
    stored_count = 0
    for b in bars:
        existing = await session.get(Bar1D, (instrument_id, b.ts))
        if existing is None:
            new_bar = Bar1D(
                instrument_id=instrument_id,
                ts=b.ts,
                open=b.open,
                high=b.high,
                low=b.low,
                close=b.close,
                volume=b.volume,
                deliv_qty=b.deliv_qty,
                adj_factor=b.adj_factor,
                source=source,
            )
            session.add(new_bar)
            stored_count += 1
        else:
            existing.open = b.open
            existing.high = b.high
            existing.low = b.low
            existing.close = b.close
            existing.volume = b.volume
            existing.deliv_qty = b.deliv_qty
            existing.adj_factor = b.adj_factor
            existing.source = source
            stored_count += 1

    await session.commit()
    return stored_count
