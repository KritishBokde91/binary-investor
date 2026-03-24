"""
Monte Carlo Portfolio Simulator — compare Disciplined SIP vs Panic Seller.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from config.settings import settings
from data.stock_data import fetch_historical_data


class PortfolioSimulator:
    """Monte Carlo simulation comparing disciplined vs. panic-driven investing."""

    def __init__(
        self,
        n_simulations: int = None,
        sip_amount: float = None,
    ):
        self.n_simulations = n_simulations or settings.MONTE_CARLO_SIMULATIONS
        self.sip_amount = sip_amount or settings.BEHAVIOR_GAP_SIP_AMOUNT

    def simulate_sip_vs_panic(
        self,
        symbol: str,
        years: int = 10,
        panic_exit_threshold: float = -0.10,
        panic_reentry_days: int = 90,
    ) -> dict:
        """
        Monte Carlo simulation comparing two investor profiles:

        1. Disciplined SIP: Monthly investment regardless of market conditions.
        2. Panic Seller: Monthly SIP but exits entirely after a 10% drawdown,
           waits 90 days in cash, then re-enters.

        Uses historical return distribution to generate simulated paths.
        """
        df = fetch_historical_data(symbol, years * 365)
        if df.empty or len(df) < 100:
            return self._fallback_simulation(years)

        # Use historical daily returns distribution
        daily_returns = df["Returns"].dropna().values
        mean_return = np.mean(daily_returns)
        std_return = np.std(daily_returns)

        trading_days = 252 * years
        monthly_trading_days = 21

        sip_results = []
        panic_results = []

        for _ in range(self.n_simulations):
            # Generate simulated returns from historical distribution
            sim_returns = np.random.normal(mean_return, std_return, trading_days)

            # Profile 1: Disciplined SIP
            sip_value = 0
            sip_units = 0
            price = 100  # Normalized start price

            for day in range(trading_days):
                price *= (1 + sim_returns[day])
                price = max(price, 0.01)

                if day % monthly_trading_days == 0:
                    sip_units += self.sip_amount / price

            sip_value = sip_units * price
            sip_results.append(sip_value)

            # Profile 2: Panic Seller
            panic_value = 0
            panic_units = 0
            panic_cash = 0
            price = 100
            peak_price = 100
            panic_days_left = 0
            in_market = True

            for day in range(trading_days):
                price *= (1 + sim_returns[day])
                price = max(price, 0.01)

                if in_market:
                    peak_price = max(peak_price, price)

                    # Check for panic exit
                    drawdown = (price - peak_price) / peak_price
                    if drawdown <= panic_exit_threshold:
                        # PANIC: EXIT - sell all units
                        panic_cash += panic_units * price
                        panic_units = 0
                        in_market = False
                        panic_days_left = panic_reentry_days

                    # Monthly SIP
                    if day % monthly_trading_days == 0:
                        panic_units += self.sip_amount / price
                else:
                    panic_days_left -= 1
                    # SIP goes to cash during panic
                    if day % monthly_trading_days == 0:
                        panic_cash += self.sip_amount

                    if panic_days_left <= 0:
                        # Re-enter market
                        in_market = True
                        peak_price = price
                        panic_units += panic_cash / price
                        panic_cash = 0

            panic_value = panic_units * price + panic_cash
            panic_results.append(panic_value)

        sip_arr = np.array(sip_results)
        panic_arr = np.array(panic_results)

        total_invested = self.sip_amount * (trading_days // monthly_trading_days)

        return {
            "total_invested": total_invested,
            "sip": {
                "mean": round(np.mean(sip_arr), 0),
                "median": round(np.median(sip_arr), 0),
                "p10": round(np.percentile(sip_arr, 10), 0),
                "p90": round(np.percentile(sip_arr, 90), 0),
                "min": round(np.min(sip_arr), 0),
                "max": round(np.max(sip_arr), 0),
                "all_results": sip_arr,
            },
            "panic": {
                "mean": round(np.mean(panic_arr), 0),
                "median": round(np.median(panic_arr), 0),
                "p10": round(np.percentile(panic_arr, 10), 0),
                "p90": round(np.percentile(panic_arr, 90), 0),
                "min": round(np.min(panic_arr), 0),
                "max": round(np.max(panic_arr), 0),
                "all_results": panic_arr,
            },
            "cost_of_panic": {
                "mean_loss": round(np.mean(sip_arr) - np.mean(panic_arr), 0),
                "median_loss": round(np.median(sip_arr) - np.median(panic_arr), 0),
                "pct_loss": round(
                    (np.mean(sip_arr) - np.mean(panic_arr)) / np.mean(sip_arr) * 100, 1
                ),
                "win_rate": round(
                    (sip_arr > panic_arr).sum() / len(sip_arr) * 100, 1
                ),
            },
            "n_simulations": self.n_simulations,
            "years": years,
            "symbol": symbol,
        }

    def _fallback_simulation(self, years: int) -> dict:
        """Fallback with Indian market average returns when data unavailable."""
        mean_return = 0.0005  # ~12.6% annualized
        std_return = 0.015    # ~23.8% annualized vol

        trading_days = 252 * years
        monthly_trading_days = 21

        sip_results = []
        panic_results = []

        for _ in range(min(self.n_simulations, 500)):
            sim_returns = np.random.normal(mean_return, std_return, trading_days)

            # SIP
            sip_units = 0
            price = 100
            for day in range(trading_days):
                price *= (1 + sim_returns[day])
                price = max(price, 0.01)
                if day % monthly_trading_days == 0:
                    sip_units += self.sip_amount / price
            sip_results.append(sip_units * price)

            # Panic Seller (simplified)
            panic_units = 0
            panic_cash = 0
            price = 100
            peak = 100
            in_market = True
            wait = 0

            for day in range(trading_days):
                price *= (1 + sim_returns[day])
                price = max(price, 0.01)

                if in_market:
                    peak = max(peak, price)
                    if (price - peak) / peak <= -0.10:
                        panic_cash += panic_units * price
                        panic_units = 0
                        in_market = False
                        wait = 90
                    if day % monthly_trading_days == 0:
                        panic_units += self.sip_amount / price
                else:
                    wait -= 1
                    if day % monthly_trading_days == 0:
                        panic_cash += self.sip_amount
                    if wait <= 0:
                        in_market = True
                        peak = price
                        panic_units += panic_cash / price
                        panic_cash = 0

            panic_results.append(panic_units * price + panic_cash)

        sip_arr = np.array(sip_results)
        panic_arr = np.array(panic_results)
        total_invested = self.sip_amount * (trading_days // monthly_trading_days)

        return {
            "total_invested": total_invested,
            "sip": {
                "mean": round(np.mean(sip_arr), 0),
                "median": round(np.median(sip_arr), 0),
                "p10": round(np.percentile(sip_arr, 10), 0),
                "p90": round(np.percentile(sip_arr, 90), 0),
                "min": round(np.min(sip_arr), 0),
                "max": round(np.max(sip_arr), 0),
                "all_results": sip_arr,
            },
            "panic": {
                "mean": round(np.mean(panic_arr), 0),
                "median": round(np.median(panic_arr), 0),
                "p10": round(np.percentile(panic_arr, 10), 0),
                "p90": round(np.percentile(panic_arr, 90), 0),
                "min": round(np.min(panic_arr), 0),
                "max": round(np.max(panic_arr), 0),
                "all_results": panic_arr,
            },
            "cost_of_panic": {
                "mean_loss": round(np.mean(sip_arr) - np.mean(panic_arr), 0),
                "median_loss": round(np.median(sip_arr) - np.median(panic_arr), 0),
                "pct_loss": round(
                    (np.mean(sip_arr) - np.mean(panic_arr)) / max(np.mean(sip_arr), 1) * 100, 1
                ),
                "win_rate": round(
                    (sip_arr > panic_arr).sum() / len(sip_arr) * 100, 1
                ),
            },
            "n_simulations": len(sip_results),
            "years": years,
            "symbol": "~NIFTY (Estimated)",
        }
