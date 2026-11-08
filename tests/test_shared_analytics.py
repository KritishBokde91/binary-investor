import pytest
import numpy as np
import pandas as pd

from sheep_or_sleep.analytics.behavior_gap import compute_behavior_gap, compute_missing_days
from sheep_or_sleep.analytics.herding import compute_cck_herding
from sheep_or_sleep.analytics.panic import compute_panic_score
from sheep_or_sleep.analytics.simulator import simulate_sip_vs_panic


def test_shared_cagr_uses_252_days():
    """Verify shared missing days analytics uses 252 trading days."""
    n_days = 2520
    target_cagr = 0.10
    daily_r = (1 + target_cagr) ** (1 / 252) - 1
    prices = [100.0 * ((1 + daily_r) ** i) for i in range(n_days + 1)]
    dates = pd.date_range("2014-01-01", periods=n_days + 1, freq="B")
    df = pd.DataFrame({"Close": prices, "Volume": [1000] * (n_days + 1)}, index=dates)
    df["Returns"] = df["Close"].pct_change()
    df_clean = df.dropna()

    res = compute_missing_days(df_clean, initial=100000)
    assert len(res) == 6
    assert res[0]["scenario"] == "Fully invested"
    assert np.isclose(res[0]["cagr"], 10.0, atol=0.1)


def test_shared_herding_one_sided_p_value_and_zero_intensity():
    """Verify shared CCK herding computes one-sided p-value and 0 intensity when not herding."""
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    np.random.seed(42)
    rm = np.random.normal(0, 0.02, 100)
    returns_dict = {
        f"STOCK_{i}": pd.Series(rm + ((-1) ** i) * (0.01 + 0.5 * (rm ** 2)), index=dates)
        for i in range(4)
    }
    res = compute_cck_herding(returns_dict, sector="Energy")
    assert res["gamma2"] > 0
    assert not res["herdingDetected"]
    assert res["intensity"] == 0.0


def test_shared_panic_lagged_window():
    """Verify shared panic scoring uses lagged volume window excluding today."""
    dates = pd.date_range("2026-01-01", periods=40, freq="B")
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

    res = compute_panic_score(df_clean)
    assert res["panicScore"] >= 0
    spike_entry = next((item for item in res["volumeData"] if item["volume"] == 200), None)
    assert spike_entry is not None
    assert spike_entry["zscore"] > 6.0


def test_shared_simulator_exit_day_ordering():
    """Verify shared Monte Carlo does not buy units on exit day."""
    trading_days = 252
    sim = np.zeros(trading_days)
    sim[21] = -0.15  # crash on monthly day
    sim[22] = -0.50  # crash next day
    res = simulate_sip_vs_panic(sim_returns=sim, years=1, sip=10000, n_sims=1)
    assert res["panic"]["median"] > 115000  # immune to day 22 crash because 100% in cash
