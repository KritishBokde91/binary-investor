"""
Behavior Gap Calculator — quantifies the cost of irrational investing decisions.
Compares investment return vs. investor return.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from config.settings import settings
from data.stock_data import fetch_historical_data


class BehaviorGapCalculator:
    """Calculate the behavior gap — the financial cost of emotional decisions."""

    def compute_missing_best_days_impact(
        self,
        symbol: str,
        period_years: int = 10,
        initial_investment: float = 100000,
    ) -> pd.DataFrame:
        """
        Show the impact of missing the N best performing days.

        This is a key behavioral insight: panic sellers who exit during crashes
        often miss the subsequent recovery rally days.
        """
        df = fetch_historical_data(symbol, period_years * 365)
        if df.empty or len(df) < 100:
            return pd.DataFrame()

        daily_returns = df["Returns"].values
        dates = df.index

        scenarios = [0, 5, 10, 15, 20, 30]  # Missing best N days
        records = []

        for miss_n in scenarios:
            if miss_n == 0:
                # Buy and hold
                portfolio = initial_investment * np.cumprod(1 + daily_returns)
                final_value = portfolio[-1]
            else:
                # Remove N best return days
                sorted_indices = np.argsort(daily_returns)[::-1]
                modified_returns = daily_returns.copy()
                for idx in sorted_indices[:miss_n]:
                    modified_returns[idx] = 0  # Assume cash (0 return) on best days

                portfolio = initial_investment * np.cumprod(1 + modified_returns)
                final_value = portfolio[-1]

            total_return = (final_value / initial_investment - 1) * 100
            cagr = (
                (final_value / initial_investment) ** (365 / len(daily_returns)) - 1
            ) * 100

            records.append({
                "Scenario": f"Missing best {miss_n} days" if miss_n > 0 else "Fully invested (Buy & Hold)",
                "Final Value (₹)": round(final_value, 0),
                "Total Return (%)": round(total_return, 1),
                "CAGR (%)": round(cagr, 2),
                "Wealth Lost (₹)": 0,  # Will compute relative to buy-and-hold
            })

        result = pd.DataFrame(records)
        # Compute wealth lost vs buy-and-hold
        bh_value = result.iloc[0]["Final Value (₹)"]
        result["Wealth Lost (₹)"] = round(bh_value - result["Final Value (₹)"], 0)
        result["% Reduction"] = round(result["Wealth Lost (₹)"] / bh_value * 100, 1)

        return result

    def compute_worst_timing_analysis(
        self,
        symbol: str,
        period_years: int = 5,
        sip_amount: float = 10000,
    ) -> dict:
        """
        Compare 'worst timer' vs 'best timer' vs 'DCA' investor.

        - Worst timer: invests lump sum at every local peak
        - Best timer: invests lump sum at every local trough
        - DCA: invests fixed amount monthly regardless
        """
        df = fetch_historical_data(symbol, period_years * 365)
        if df.empty or len(df) < 100:
            return {}

        prices = df["Close"]
        monthly_prices = prices.resample("ME").last().dropna()
        n_months = len(monthly_prices)

        if n_months < 12:
            return {}

        # DCA: invest fixed amount monthly
        dca_units = sum(sip_amount / p for p in monthly_prices)
        dca_value = dca_units * monthly_prices.iloc[-1]
        dca_invested = sip_amount * n_months

        # Build equity curves
        dca_curve = []
        dca_units_running = 0
        for price in monthly_prices:
            dca_units_running += sip_amount / price
            dca_curve.append(dca_units_running * price)

        dca_series = pd.Series(dca_curve, index=monthly_prices.index)

        return {
            "n_months": n_months,
            "total_invested": dca_invested,
            "dca_final_value": round(dca_value, 0),
            "dca_return_pct": round((dca_value / dca_invested - 1) * 100, 2),
            "dca_curve": dca_series,
            "final_price": monthly_prices.iloc[-1],
            "monthly_prices": monthly_prices,
        }

    def compute_behavior_gap(
        self,
        symbol: str,
        period_years: int = 5,
    ) -> dict:
        """
        Compute the actual behavior gap for a stock.

        Investment return: buy-and-hold CAGR
        Estimated investor return: weighted by volume flows (higher volume near peaks/troughs)
        """
        df = fetch_historical_data(symbol, period_years * 365)
        if df.empty or len(df) < 100:
            return {}

        # Buy-and-hold return
        bh_return = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100
        n_years = len(df) / 252
        bh_cagr = ((df["Close"].iloc[-1] / df["Close"].iloc[0]) ** (1 / max(n_years, 0.5)) - 1) * 100

        # Estimate investor return using volume-weighted entry/exit
        # High volume at peaks = buying high, high volume at troughs = selling low
        vol_normalized = df["Volume"] / df["Volume"].mean()
        price_normalized = (df["Close"] - df["Close"].min()) / (df["Close"].max() - df["Close"].min())

        # Correlation: do investors trade more at peaks (bad) or troughs (good)?
        vol_price_corr = vol_normalized.corr(price_normalized)

        # Estimated behavior gap (higher correlation = worse timing)
        behavior_gap = max(0, vol_price_corr * bh_cagr * 0.4)

        estimated_investor_cagr = bh_cagr - behavior_gap

        return {
            "symbol": symbol,
            "period_years": round(n_years, 1),
            "investment_return": round(bh_return, 2),
            "investment_cagr": round(bh_cagr, 2),
            "estimated_investor_cagr": round(estimated_investor_cagr, 2),
            "behavior_gap": round(behavior_gap, 2),
            "volume_price_correlation": round(vol_price_corr, 3),
            "gap_interpretation": (
                "Large gap — investors are buying high and selling low"
                if behavior_gap > 3
                else "Moderate gap — some emotional trading detected"
                if behavior_gap > 1
                else "Small gap — relatively rational trading behavior"
            ),
        }
