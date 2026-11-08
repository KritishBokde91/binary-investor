"""
Unit and integration tests for /api/analyze robustness and JSON serialization.
Verifies that 500 errors are prevented across cache, analytics, and route handlers.
"""

from __future__ import annotations

import json
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from unittest.mock import patch
from fastapi.testclient import TestClient

from server import app, get_price_chart
from sheep_or_sleep.cache.service import CacheService, _sanitize_for_json


def test_sanitize_for_json_converts_numpy_and_nan():
    payload = {
        "int_val": np.int64(42),
        "float_val": np.float64(3.1415),
        "nan_val": float("nan"),
        "inf_val": float("inf"),
        "arr": np.array([1, 2, 3]),
        "nested": {
            "bool_val": np.bool_(True),
            "date_val": datetime(2026, 11, 8, tzinfo=timezone.utc),
        },
    }
    sanitized = _sanitize_for_json(payload)
    # Must dump without throwing TypeError
    dumped = json.dumps(sanitized)
    assert dumped is not None
    loaded = json.loads(dumped)
    assert loaded["int_val"] == 42
    assert loaded["nan_val"] == 0.0
    assert loaded["inf_val"] == 0.0
    assert loaded["arr"] == [1, 2, 3]
    assert loaded["nested"]["bool_val"] is True


def test_get_price_chart_handles_nan_and_missing_values():
    dates = pd.date_range("2025-01-01", periods=10, freq="B")
    df = pd.DataFrame(
        {
            "Open": [100.0, np.nan, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0],
            "High": [105.0, 106.0, np.nan, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0],
            "Low": [95.0, 96.0, 97.0, np.nan, 99.0, 100.0, 101.0, 102.0, 103.0, 104.0],
            "Close": [102.0, 103.0, 104.0, 105.0, np.nan, 107.0, 108.0, 109.0, 110.0, 111.0],
            "Volume": [1000, np.nan, 3000, 4000, 5000, np.nan, 7000, 8000, 9000, 10000],
        },
        index=dates,
    )
    with patch("server.fetch_historical", return_value=df):
        chart = get_price_chart("TCS.NS", 10)
        assert len(chart) > 0
        for pt in chart:
            assert isinstance(pt["volume"], int)
            assert not np.isnan(pt["open"])
            assert not np.isnan(pt["close"])


def test_analyze_recovers_price_from_history_when_quote_throttled():
    client = TestClient(app)
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    prices = np.linspace(1000, 1500, 100)
    df = pd.DataFrame(
        {
            "Open": prices - 5,
            "High": prices + 10,
            "Low": prices - 10,
            "Close": prices,
            "Volume": np.random.randint(1000, 5000, size=100),
            "Returns": pd.Series(prices).pct_change().fillna(0).values,
        },
        index=dates,
    )
    # Quote with 0 price (simulating throttled yf.Ticker.info)
    mock_quote = {"symbol": "INFY.NS", "name": "Infosys", "price": 0, "prevClose": 0}

    with patch("server.fetch_historical", return_value=df), patch("server.fetch_quote", return_value=mock_quote):
        resp = client.post("/api/analyze", json={"symbol": "INFY.NS"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["quote"]["price"] == 1500.0
        assert data["status"] in ("ok", "degraded")
