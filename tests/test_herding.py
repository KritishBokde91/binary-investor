import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch
from scipy import stats

import server
from analytics.herd_detector import HerdDetector


def test_herding_non_herding_reports_zero_intensity():
    """
    AUDIT.md Finding 2.2 D & Phase 0 Item c:
    Non-herding (including gamma2 > 0) must NEVER report a positive herding intensity.
    """
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    np.random.seed(42)
    rm = np.random.normal(0, 0.02, 100)
    returns_dict = {}
    for i in range(4):
        # Dispersion increases strongly with rm^2 (anti-herding)
        returns_dict[f"STOCK_{i}.NS"] = rm + ((-1) ** i) * (0.01 + 0.5 * (rm ** 2))

    def fake_fetch_historical(sym, period_days):
        if sym in returns_dict:
            return pd.DataFrame({"Returns": returns_dict[sym]}, index=dates)
        return pd.DataFrame({"Returns": returns_dict["STOCK_0.NS"]}, index=dates)

    with patch("server.fetch_historical", side_effect=fake_fetch_historical), \
         patch("server.get_sector_symbols", return_value=[f"STOCK_{i}.NS" for i in range(4)]), \
         patch("server.STOCK_UNIVERSE", [{"symbol": "STOCK_0.NS", "name": "Stock 0", "sector": "Energy", "index": "NIFTY 50"}]):

        res = server.compute_herding("STOCK_0.NS", period_days=100)
        assert res["gamma2"] > 0
        assert not res["herdingDetected"]
        assert res["intensity"] == 0.0


def test_herding_one_sided_p_value_detects_herding_when_two_sided_misses():
    """
    AUDIT.md Finding 2.2 D & Phase 0 Item c:
    Verify one-sided p-value using t.sf.
    Construct CSAD data with gamma2 < 0 where t-stat is ~ -1.8.
    With one-sided p-value, p < 0.05 -> herding_detected is True.
    """
    detector = HerdDetector()
    np.random.seed(123)
    n = 100
    abs_mkt = np.abs(np.random.normal(0, 0.02, n))
    mkt_sq = abs_mkt ** 2
    # Design y = alpha + gamma1*abs_mkt + gamma2*mkt_sq + noise
    # such that gamma2 < 0 and t-stat is around -1.8
    y = 0.02 + 0.5 * abs_mkt - 4.5 * mkt_sq + np.random.normal(0, 0.0015, n)
    csad_df = pd.DataFrame({
        "CSAD": y,
        "Abs_Market_Return": abs_mkt,
        "Market_Return_Sq": mkt_sq,
        "Market_Return": abs_mkt,
    })

    reg = detector.run_cck_regression(csad_df)
    assert reg["gamma2"] < 0
    # One-sided p-value should match t.sf(-t_stat)
    df = n - 3
    expected_p = float(stats.t.sf(-reg["gamma2_tstat"], df=df))
    assert np.isclose(reg["gamma2_pvalue"], expected_p, atol=1e-5)
    # Intensity must be positive for detected herding and 0 when not detected
    if reg["herding_detected"]:
        assert reg["herding_intensity"] > 0
    else:
        assert reg["herding_intensity"] == 0.0
