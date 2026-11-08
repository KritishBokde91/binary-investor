"""Pydantic response models for all API routes (Phase 1 Step 5)."""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel


class LivenessResponse(BaseModel):
    status: str = "ok"


class ReadinessResponse(BaseModel):
    status: str
    postgres: str
    redis: str


class MetricsResponse(BaseModel):
    hits: int
    misses: int
    stale_hits: int
    stampedes_prevented: int
    hit_ratio: float


class StockListResponse(BaseModel):
    stocks: list[dict[str, Any]]


class QuoteResponse(BaseModel):
    price: float
    change: float
    change_percent: float
    as_of: Optional[str] = None


class AnalyzeResponse(BaseModel):
    status: str
    as_of: str
    data_version: str
    reason: Optional[str] = None
    quote: dict[str, Any]
    priceChart: list[dict[str, Any]]
    herding: dict[str, Any]
    panic: dict[str, Any]
    behaviorGap: dict[str, Any]
    missingDays: list[dict[str, Any]]
    monteCarlo: dict[str, Any]


class ChatResponse(BaseModel):
    response: str


class HealthResponse(BaseModel):
    status: str
    groq: bool
