import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch

import server
from analytics.panic_detector import PanicDetector


def test_panic_volume_zscore_uses_lagged_window_excluding_today():
    """
    AUDIT.md Finding 2.2 E & Phase 0 Item e:
    Volume z-score in compute_panic must use a lagged window (exclude today).
    For a baseline of 30 prior days with mean=100, std=10, and today volume=200:
    - Lagged z-score: (200 - 100) / 10 = 10.0
    - Contaminated unlagged z-score (including today): ~3.90 (mathematical saturation)
    """
    # 40 days of data
    dates = pd.date_range("2026-01-01", periods=40, freq="B")
    # First 30 days: alternating 90 and 110 (mean = 100, std ~ 10.17)
    # Day 31: volume = 200 (a massive 10-sigma volume spike), return = -2%
    vols = [90, 110] * 15 + [200] + [100] * 9
    prices = [100.0] * 30 + [98.0] * 10

    df = pd.DataFrame({
        "Open": prices,
        "High": [p * 1.01 for p in prices],
        "Low": [p * 0.99 for p in prices],
        "Close": prices,
        "Volume": vols,
    }, index=dates)
    df["Returns"] = df["Close"].pct_change()
    df_clean = df.dropna().copy()

    # Test server.compute_panic
    with patch("server.fetch_historical", return_value=df_clean):
        panic_res = server.compute_panic("TEST.NS", period_days=90)
        vol_data = panic_res["volumeData"]
        assert len(vol_data) > 0
        spike_entry = next((item for item in vol_data if item["volume"] == 200), None)
        assert spike_entry is not None, "Could not find volume=200 entry in volumeData"
        # Lagged z-score should be ~ 9.8 (> 6.0)
        assert spike_entry["zscore"] > 6.0, (
            f"Volume z-score on spike day was contaminated: got {spike_entry['zscore']}, expected > 6.0 (lagged window)"
        )

    # Test analytics/panic_detector.py PanicDetector.detect_volume_anomalies
    detector = PanicDetector(volume_zscore_threshold=2.0)
    anomalies = detector.detect_volume_anomalies(df_clean)
    assert not anomalies.empty
    spike_row = anomalies[anomalies["Volume"] == 200]
    assert not spike_row.empty
    zscore_val = float(spike_row["Volume_Zscore"].iloc[0])
    assert zscore_val > 6.0, (
        f"PanicDetector volume z-score was contaminated: got {zscore_val}, expected > 6.0"
    )
