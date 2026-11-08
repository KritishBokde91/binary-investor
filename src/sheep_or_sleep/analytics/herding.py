"""
CCK Herding Detector (Chang, Cheng & Khorana, 2000).
Quadratic regression of CSAD against market return:
CSAD = alpha + gamma1 * |Rm| + gamma2 * Rm^2
Herding is present when gamma2 < 0 at p < 0.05 (one-sided t-test).
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats


def compute_cck_herding(returns_dict: dict[str, pd.Series], sector: str = "Unknown") -> dict:
    """
    Compute cross-sectional absolute deviation (CSAD) regression across peer returns.
    """
    if len(returns_dict) < 3:
        return {
            "herdingDetected": False,
            "intensity": 0.0,
            "gamma2": 0.0,
            "pValue": 1.0,
            "rSquared": 0.0,
            "csadData": [],
            "sector": sector,
            "error": "Need ≥3 stocks in sector",
        }

    returns_df = pd.DataFrame(returns_dict).dropna()
    if len(returns_df) < 30:
        return {
            "herdingDetected": False,
            "intensity": 0.0,
            "gamma2": 0.0,
            "pValue": 1.0,
            "rSquared": 0.0,
            "csadData": [],
            "sector": sector,
            "error": "Insufficient observations (<30 days)",
        }

    market_return = returns_df.mean(axis=1)
    csad = returns_df.sub(market_return, axis=0).abs().mean(axis=1)
    abs_mkt = market_return.abs()
    mkt_sq = market_return ** 2

    y = csad.values
    X = np.column_stack([np.ones(len(y)), abs_mkt.values, mkt_sq.values])

    try:
        beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        alpha, gamma1, gamma2 = beta
        y_pred = X @ beta
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        n, k = len(y), 3
        mse = ss_res / (n - k)

        try:
            cov = mse * np.linalg.inv(X.T @ X)
            se = np.sqrt(np.diag(cov))
        except Exception:
            se = np.array([0.0, 0.0, 0.0])

        t_stat = gamma2 / se[2] if se[2] > 0 else 0.0
        # Phase 0 fix: one-sided lower tail test for gamma2 < 0
        p_val = float(stats.t.sf(-t_stat, df=n - k))
        herding = gamma2 < 0 and p_val < 0.05
        # Phase 0 fix: zero intensity when herding is False (including gamma2 > 0)
        intensity = min(100.0, abs(gamma2 / max(abs(gamma1), 1e-6)) * 100) if herding else 0.0

        indices = np.linspace(0, len(abs_mkt) - 1, min(200, len(abs_mkt)), dtype=int)
        csad_data = [
            {
                "absReturn": round(float(abs_mkt.iloc[i]), 6),
                "csad": round(float(csad.iloc[i]), 6),
                "mktReturn": round(float(market_return.iloc[i]), 6),
                "fitted": round(float(y_pred[i]), 6),
            }
            for i in indices
        ]

        return {
            "sector": sector,
            "nStocks": len(returns_dict),
            "herdingDetected": bool(herding),
            "intensity": round(float(intensity), 1),
            "gamma2": round(float(gamma2), 6),
            "gamma1": round(float(gamma1), 6),
            "alpha": round(float(alpha), 6),
            "pValue": round(float(p_val), 6),
            "tStat": round(float(t_stat), 4),
            "rSquared": round(float(r_sq), 4),
            "observations": n,
            "csadData": csad_data,
        }
    except Exception as e:
        return {
            "herdingDetected": False,
            "intensity": 0.0,
            "gamma2": 0.0,
            "pValue": 1.0,
            "rSquared": 0.0,
            "csadData": [],
            "sector": sector,
            "error": str(e),
        }
