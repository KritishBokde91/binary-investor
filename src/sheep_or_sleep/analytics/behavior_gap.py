"""
Behavior Gap & Missing-Best-Days Analytics.
Quantifies return loss from mistimed entries/exits and missed top market days.
"""

from __future__ import annotations
import numpy as np
import pandas as pd


def compute_behavior_gap(df: pd.DataFrame) -> dict:
    """
    Compute behavior gap heuristic:
    gap = max(0, corr(volume, price) * buy_and_hold_cagr * 0.4)
    """
    if df.empty or len(df) < 100:
        return {
            "investmentReturn": 0.0,
            "investmentCagr": 0.0,
            "investorCagr": 0.0,
            "behaviorGap": 0.0,
            "periodYears": 0.0,
            "gapInterpretation": "Insufficient data",
        }

    bh_return = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100
    n_years = len(df) / 252
    bh_cagr = ((df["Close"].iloc[-1] / df["Close"].iloc[0]) ** (252 / max(len(df), 126)) - 1) * 100

    vol_normalized = df["Volume"] / df["Volume"].mean()
    price_span = df["Close"].max() - df["Close"].min()
    price_normalized = (df["Close"] - df["Close"].min()) / price_span if price_span > 0 else df["Close"] * 0
    corr = float(vol_normalized.corr(price_normalized))
    if np.isnan(corr):
        corr = 0.0
    gap = max(0.0, corr * bh_cagr * 0.4)
    investor_cagr = bh_cagr - gap

    if gap > 3:
        interp = "Large gap — investors are buying high and selling low"
    elif gap > 1:
        interp = "Moderate gap — some emotional trading detected"
    else:
        interp = "Small gap — relatively rational trading behavior"

    return {
        "investmentReturn": round(float(bh_return), 2),
        "investmentCagr": round(float(bh_cagr), 2),
        "investorCagr": round(float(investor_cagr), 2),
        "behaviorGap": round(float(gap), 2),
        "periodYears": round(float(n_years), 1),
        "gapInterpretation": interp,
    }


def compute_missing_days(df: pd.DataFrame, initial: float = 100000.0) -> list[dict]:
    """
    Compute Missing Best Days analysis using 252 trading days/year for CAGR.
    """
    if df.empty or len(df) < 100 or "Returns" not in df.columns:
        return []

    daily_returns = df["Returns"].dropna().values
    if len(daily_returns) < 100:
        return []

    scenarios = [0, 5, 10, 15, 20, 30]
    results = []
    bh_final = initial * np.prod(1 + daily_returns)

    for miss_n in scenarios:
        modified = daily_returns.copy()
        if miss_n > 0:
            top_indices = np.argsort(daily_returns)[::-1][:miss_n]
            for idx in top_indices:
                modified[idx] = 0.0

        final = initial * np.prod(1 + modified)
        total_ret = (final / initial - 1) * 100
        # Audit Finding 3 / Phase 0: 252 trading days per year
        cagr = ((final / initial) ** (252 / len(daily_returns)) - 1) * 100

        results.append({
            "scenario": f"Missing {miss_n} best days" if miss_n > 0 else "Fully invested",
            "finalValue": round(float(final), 0),
            "totalReturn": round(float(total_ret), 1),
            "cagr": round(float(cagr), 2),
            "reduction": round(float((bh_final - final) / bh_final * 100), 1) if miss_n > 0 else 0.0,
        })

    return results
