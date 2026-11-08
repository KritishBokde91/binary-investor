import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch

import server
from analytics.behavior_gap import BehaviorGapCalculator


def test_cagr_constant_growth_series_in_server_and_behavior_gap():
    """
    AUDIT.md Finding 3 & Phase 0 Item b:
    Test with a known constant-growth series.
    True annual CAGR is 10.0%.
    Using 252 trading days per year, CAGR for 'Fully invested' must be 10.0% (within 0.1%).
    The bug (365 / len) yields ~14.86%.
    """
    n_days = 2520
    target_cagr = 0.10  # 10% annual CAGR
    daily_r = (1 + target_cagr) ** (1 / 252) - 1

    prices = [100.0 * ((1 + daily_r) ** i) for i in range(n_days + 1)]
    dates = pd.date_range(start="2014-01-01", periods=n_days + 1, freq="B")
    df = pd.DataFrame({
        "Open": prices,
        "High": prices,
        "Low": prices,
        "Close": prices,
        "Volume": [1000000] * (n_days + 1),
    }, index=dates)
    df["Returns"] = df["Close"].pct_change()
    df_clean = df.dropna()

    # 1. Test server.py compute_missing_days
    with patch("server.fetch_historical", return_value=df_clean):
        server_res = server.compute_missing_days("TEST.NS", period_years=10, initial=100000)
        assert len(server_res) > 0
        fully_invested = server_res[0]
        assert fully_invested["scenario"] == "Fully invested"
        # We assert CAGR is approx 10.0%, NOT ~14.86%
        assert np.isclose(fully_invested["cagr"], 10.0, atol=0.1), (
            f"Expected server CAGR ~10.0%, got {fully_invested['cagr']}% (365/len bug)"
        )

    # 2. Test analytics/behavior_gap.py compute_missing_best_days_impact
    with patch("analytics.behavior_gap.fetch_historical_data", return_value=df_clean):
        calculator = BehaviorGapCalculator()
        bg_res = calculator.compute_missing_best_days_impact("TEST.NS", period_years=10, initial_investment=100000)
        assert not bg_res.empty
        bg_fully_invested_cagr = bg_res.iloc[0]["CAGR (%)"]
        assert np.isclose(bg_fully_invested_cagr, 10.0, atol=0.1), (
            f"Expected BehaviorGap CAGR ~10.0%, got {bg_fully_invested_cagr}% (365/len bug)"
        )
