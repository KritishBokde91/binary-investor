"""
CCK Model Implementation — Cross-Sectional Absolute Deviation (CSAD) based
herding detection using the Chang, Cheng & Khorana methodology.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
import streamlit as st

from config.settings import settings
from data.stock_data import fetch_historical_data
from config.stock_universe import get_sector_symbols, get_all_sectors


class HerdDetector:
    """Detect herding behavior in Indian stock sectors using the CCK model."""

    def __init__(self, period_days: int = 365, window: int = None):
        self.period_days = period_days
        self.window = window or settings.HERDING_WINDOW

    def compute_csad(self, returns_df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute Cross-Sectional Absolute Deviation (CSAD).

        CSAD_t = (1/N) * Σ |R_i,t - R_m,t|

        Where R_m,t is the cross-sectional average (equal-weighted market return).
        """
        if returns_df.empty or returns_df.shape[1] < 3:
            return pd.DataFrame()

        # Equal-weighted market return
        market_return = returns_df.mean(axis=1)

        # CSAD: mean absolute deviation from market return
        csad = returns_df.sub(market_return, axis=0).abs().mean(axis=1)

        result = pd.DataFrame({
            "Market_Return": market_return,
            "Abs_Market_Return": market_return.abs(),
            "Market_Return_Sq": market_return ** 2,
            "CSAD": csad,
        })

        return result.dropna()

    def compute_cssd(self, returns_df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute Cross-Sectional Standard Deviation (CSSD).

        CSSD_t = sqrt( (1/(N-1)) * Σ (R_i,t - R_m,t)^2 )
        """
        if returns_df.empty or returns_df.shape[1] < 3:
            return pd.DataFrame()

        market_return = returns_df.mean(axis=1)
        cssd = returns_df.sub(market_return, axis=0).pow(2).mean(axis=1).pow(0.5)

        result = pd.DataFrame({
            "Market_Return": market_return,
            "CSSD": cssd,
        })
        return result.dropna()

    def run_cck_regression(self, csad_df: pd.DataFrame) -> dict:
        """
        Run CCK quadratic regression:
        CSAD_t = α + γ₁ |R_m,t| + γ₂ R²_m,t + ε_t

        If γ₂ < 0 and statistically significant → evidence of herding.
        """
        if csad_df.empty or len(csad_df) < 30:
            return self._empty_regression_result()

        y = csad_df["CSAD"].values
        x1 = csad_df["Abs_Market_Return"].values
        x2 = csad_df["Market_Return_Sq"].values

        # Add constant
        X = np.column_stack([np.ones(len(x1)), x1, x2])

        try:
            # OLS regression
            beta, residuals, rank, sv = np.linalg.lstsq(X, y, rcond=None)

            alpha, gamma1, gamma2 = beta

            # Compute statistics
            y_pred = X @ beta
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

            n = len(y)
            k = 3  # number of parameters
            mse = ss_res / (n - k)

            # Standard errors
            try:
                cov = mse * np.linalg.inv(X.T @ X)
                se = np.sqrt(np.diag(cov))
            except np.linalg.LinAlgError:
                se = np.array([0, 0, 0])

            # T-statistics and p-values for γ₂
            t_stat_gamma2 = gamma2 / se[2] if se[2] > 0 else 0
            p_value_gamma2 = 2 * (1 - stats.t.cdf(abs(t_stat_gamma2), df=n - k))

            # Herding detection
            herding_detected = gamma2 < 0 and p_value_gamma2 < 0.05

            # Herding intensity (0-100)
            if herding_detected:
                intensity = min(100, abs(gamma2 / max(abs(gamma1), 1e-6)) * 100)
            else:
                intensity = max(0, min(20, abs(gamma2) * 1000))

            return {
                "alpha": round(alpha, 6),
                "gamma1": round(gamma1, 6),
                "gamma2": round(gamma2, 6),
                "gamma2_se": round(se[2], 6),
                "gamma2_tstat": round(t_stat_gamma2, 4),
                "gamma2_pvalue": round(p_value_gamma2, 6),
                "r_squared": round(r_squared, 4),
                "n_observations": n,
                "herding_detected": herding_detected,
                "herding_intensity": round(intensity, 1),
                "y_pred": y_pred,
            }

        except Exception as e:
            return self._empty_regression_result()

    def _empty_regression_result(self):
        return {
            "alpha": 0, "gamma1": 0, "gamma2": 0,
            "gamma2_se": 0, "gamma2_tstat": 0, "gamma2_pvalue": 1,
            "r_squared": 0, "n_observations": 0,
            "herding_detected": False, "herding_intensity": 0,
            "y_pred": np.array([]),
        }

    def rolling_herding_intensity(self, csad_df: pd.DataFrame) -> pd.Series:
        """Compute rolling γ₂ to track herding intensity over time."""
        if csad_df.empty or len(csad_df) < self.window + 10:
            return pd.Series(dtype=float)

        gamma2_series = []
        dates = []

        for i in range(self.window, len(csad_df)):
            window_df = csad_df.iloc[i - self.window:i]
            result = self.run_cck_regression(window_df)
            # Negative γ₂ means herding; we negate and clip for a 0-100 score
            intensity = max(0, min(100, -result["gamma2"] * 10000))
            gamma2_series.append(intensity)
            dates.append(csad_df.index[i])

        return pd.Series(gamma2_series, index=dates, name="Herding_Intensity")

    @st.cache_data(ttl=settings.CACHE_TTL_HISTORICAL, show_spinner=False)
    def analyze_sector(_self, sector: str) -> dict:
        """Full herding analysis for a sector."""
        symbols = get_sector_symbols(sector)
        if len(symbols) < 3:
            return {"error": f"Need ≥3 stocks for cross-sectional analysis, sector {sector} has {len(symbols)}"}

        # Fetch returns for all stocks in sector
        returns_dict = {}
        for sym in symbols:
            df = fetch_historical_data(sym, _self.period_days)
            if not df.empty and "Returns" in df.columns:
                returns_dict[sym] = df["Returns"]

        if len(returns_dict) < 3:
            return {"error": "Insufficient data for cross-sectional analysis"}

        returns_df = pd.DataFrame(returns_dict).dropna()

        # Compute CSAD
        csad_df = _self.compute_csad(returns_df)
        if csad_df.empty:
            return {"error": "Could not compute CSAD"}

        # Run regression
        regression = _self.run_cck_regression(csad_df)

        # Rolling intensity
        rolling = _self.rolling_herding_intensity(csad_df)

        return {
            "sector": sector,
            "n_stocks": len(returns_dict),
            "csad_df": csad_df,
            "regression": regression,
            "rolling_intensity": rolling,
            "returns_df": returns_df,
        }

    @st.cache_data(ttl=settings.CACHE_TTL_HISTORICAL, show_spinner=False)
    def cross_sector_comparison(_self) -> pd.DataFrame:
        """Compare herding intensity across all sectors."""
        records = []
        for sector in get_all_sectors():
            symbols = get_sector_symbols(sector)
            if len(symbols) < 3:
                continue

            result = _self.analyze_sector(sector)
            if "error" not in result:
                reg = result["regression"]
                records.append({
                    "Sector": sector,
                    "γ₂ Coefficient": reg["gamma2"],
                    "P-value": reg["gamma2_pvalue"],
                    "Herding Detected": "✅ Yes" if reg["herding_detected"] else "❌ No",
                    "Intensity (0-100)": reg["herding_intensity"],
                    "R²": reg["r_squared"],
                    "Stocks": result["n_stocks"],
                })

        df = pd.DataFrame(records)
        if not df.empty:
            df = df.sort_values("Intensity (0-100)", ascending=False).reset_index(drop=True)
        return df
