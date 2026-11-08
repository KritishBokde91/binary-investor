"""Result envelope and market data types (Phase 0 envelope & Phase 1 Step 3)."""

from __future__ import annotations

import datetime
from typing import Generic, Literal, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    """Standardized response envelope across providers, caches, and API routes."""
    status: Literal["ok", "stale", "degraded", "unavailable"]
    as_of: Optional[datetime.datetime] = None
    data_version: str = Field(default_factory=lambda: datetime.date.today().isoformat())
    value: Optional[T] = None
    reason: Optional[str] = None


class BarData(BaseModel):
    """Normalized OHLCV bar for market data."""
    ts: datetime.date
    open: float
    high: float
    low: float
    close: float
    volume: int
    deliv_qty: Optional[int] = None
    adj_factor: float = 1.0


class QuoteData(BaseModel):
    """Real-time / latest quote data for a symbol."""
    price: float
    change: float
    change_percent: float
    as_of: datetime.datetime
