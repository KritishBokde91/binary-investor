"""
Panic selling detection — volume spikes, delivery %, price-volume divergence.
Multi-factor panic scoring system.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from config.settings import settings
from data.stock_data import fetch_historical_data, compute_technical_indicators


class PanicDetector:
    """Detect panic selling signals using multiple technical and behavioral factors."""

    def __init__(
        self,
        volume_zscore_threshold: float = None,
        delivery_threshold: float = None,
    ):
        self.vol_z_thresh = volume_zscore_threshold or settings.PANIC_VOLUME_ZSCORE
        self.delivery_thresh = delivery_threshold or settings.PANIC_DELIVERY_THRESHOLD

    def detect_volume_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify days with abnormal volume spikes, especially during down moves.
        Volume Z-score > threshold on negative return days = panic signal.
        """
        if df.empty or len(df) < 21:
            return pd.DataFrame()

        result = df[["Close", "Volume", "Returns"]].copy()

        # Volume z-score
        vol_mean = result["Volume"].rolling(20).mean()
        vol_std = result["Volume"].rolling(20).std()
        result["Volume_Zscore"] = (result["Volume"] - vol_mean) / vol_std.replace(0, np.nan)

        # Flag anomalies: high volume + negative return
        result["Volume_Spike"] = result["Volume_Zscore"] > self.vol_z_thresh
        result["Panic_Volume"] = result["Volume_Spike"] & (result["Returns"] < -0.005)

        # Asymmetry: ratio of volume spikes on down days vs up days
        down_spikes = result[result["Panic_Volume"]].shape[0]
        up_spikes = result[result["Volume_Spike"] & (result["Returns"] > 0.005)].shape[0]
        result.attrs["volume_asymmetry"] = round(
            down_spikes / max(up_spikes, 1), 2
        )
        result.attrs["panic_days"] = down_spikes

        return result.dropna()

    def estimate_delivery_pressure(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Estimate delivery pressure using volume patterns.
        Low delivery (speculative) on down days = panic selling.
        We proxy delivery % using intraday price range vs volume patterns.
        """
        if df.empty or len(df) < 10:
            return pd.DataFrame()

        result = df[["Open", "High", "Low", "Close", "Volume", "Returns"]].copy()

        # Proxy: intraday range relative to close (higher range = more speculation)
        result["Intraday_Range"] = (result["High"] - result["Low"]) / result["Close"] * 100
        result["Avg_Range"] = result["Intraday_Range"].rolling(20).mean()

        # Speculative intensity: high range + high volume + negative return
        result["Speculative_Score"] = (
            result["Intraday_Range"] / result["Avg_Range"].replace(0, np.nan)
        ).clip(0, 5)

        # Proxy delivery % (inverse of speculation)
        result["Est_Delivery_Pct"] = np.clip(
            100 - result["Speculative_Score"] * 20, 10, 90
        )

        result["Low_Delivery"] = result["Est_Delivery_Pct"] < self.delivery_thresh

        return result.dropna()

    def detect_price_volume_divergence(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify price-volume divergence:
        - Price falling + Volume rising sharply = panic selling
        - Price rising + Volume falling = distribution / weak rally
        """
        if df.empty or len(df) < 21:
            return pd.DataFrame()

        result = df[["Close", "Volume", "Returns"]].copy()

        # 5-day momentum
        result["Price_Mom_5"] = result["Close"].pct_change(5)
        result["Vol_Mom_5"] = result["Volume"].pct_change(5)

        # Divergence: price down + volume up
        result["Panic_Divergence"] = (
            (result["Price_Mom_5"] < -0.03) &  # Price down >3%
            (result["Vol_Mom_5"] > 0.3)          # Volume up >30%
        )

        # Weak rally: price up + volume down
        result["Weak_Rally"] = (
            (result["Price_Mom_5"] > 0.03) &
            (result["Vol_Mom_5"] < -0.2)
        )

        return result.dropna()

    def compute_panic_score(self, symbol: str, period_days: int = 90) -> dict:
        """
        Compute multi-factor panic score (0-100) for a stock.

        Factors:
        1. Volume anomaly frequency (weight: 30%)
        2. Delivery pressure (weight: 20%)
        3. Price-volume divergence (weight: 25%)
        4. Recent drawdown severity (weight: 15%)
        5. Volatility regime (weight: 10%)
        """
        df = fetch_historical_data(symbol, period_days)
        if df.empty or len(df) < 30:
            return self._empty_panic_result(symbol)

        df = compute_technical_indicators(df)

        # Factor 1: Volume anomalies
        vol_df = self.detect_volume_anomalies(df)
        if not vol_df.empty:
            panic_vol_ratio = vol_df["Panic_Volume"].sum() / max(len(vol_df), 1)
            score_volume = min(100, panic_vol_ratio * 500)  # Scale to 0-100
        else:
            score_volume = 0

        # Factor 2: Delivery pressure
        del_df = self.estimate_delivery_pressure(df)
        if not del_df.empty:
            low_del_ratio = del_df["Low_Delivery"].sum() / max(len(del_df), 1)
            score_delivery = min(100, low_del_ratio * 200)
        else:
            score_delivery = 0

        # Factor 3: Price-volume divergence
        div_df = self.detect_price_volume_divergence(df)
        if not div_df.empty:
            div_ratio = div_df["Panic_Divergence"].sum() / max(len(div_df), 1)
            score_divergence = min(100, div_ratio * 500)
        else:
            score_divergence = 0

        # Factor 4: Recent drawdown
        if "Close" in df.columns:
            peak = df["Close"].expanding().max()
            drawdown = (df["Close"] / peak - 1) * 100
            max_drawdown = abs(drawdown.min())
            current_dd = abs(drawdown.iloc[-1])
            score_drawdown = min(100, current_dd * 5)  # 20% DD → score 100
        else:
            score_drawdown = 0
            max_drawdown = 0
            current_dd = 0

        # Factor 5: Volatility
        if "Volatility_20" in df.columns and not df["Volatility_20"].dropna().empty:
            current_vol = df["Volatility_20"].iloc[-1]
            avg_vol = df["Volatility_20"].mean()
            score_volatility = min(100, max(0, (current_vol / max(avg_vol, 1) - 1) * 100))
        else:
            score_volatility = 0
            current_vol = 0
            avg_vol = 0

        # Weighted composite score
        panic_score = (
            score_volume * 0.30 +
            score_delivery * 0.20 +
            score_divergence * 0.25 +
            score_drawdown * 0.15 +
            score_volatility * 0.10
        )
        panic_score = round(min(100, max(0, panic_score)), 1)

        # Determine level
        if panic_score >= 70:
            level = "EXTREME PANIC"
            color = "#FF1744"
        elif panic_score >= 50:
            level = "HIGH PANIC"
            color = "#FF6D00"
        elif panic_score >= 30:
            level = "MODERATE"
            color = "#FFC107"
        elif panic_score >= 10:
            level = "LOW"
            color = "#4CAF50"
        else:
            level = "CALM"
            color = "#00E676"

        return {
            "symbol": symbol,
            "panic_score": panic_score,
            "level": level,
            "color": color,
            "factors": {
                "Volume Anomaly": round(score_volume, 1),
                "Delivery Pressure": round(score_delivery, 1),
                "Price-Vol Divergence": round(score_divergence, 1),
                "Drawdown Severity": round(score_drawdown, 1),
                "Volatility Regime": round(score_volatility, 1),
            },
            "details": {
                "max_drawdown": round(max_drawdown, 2),
                "current_drawdown": round(current_dd, 2),
                "volume_anomaly_data": vol_df,
                "divergence_data": div_df,
            },
            "raw_data": df,
        }

    def _empty_panic_result(self, symbol):
        return {
            "symbol": symbol,
            "panic_score": 0,
            "level": "NO DATA",
            "color": "#9E9E9E",
            "factors": {
                "Volume Anomaly": 0,
                "Delivery Pressure": 0,
                "Price-Vol Divergence": 0,
                "Drawdown Severity": 0,
                "Volatility Regime": 0,
            },
            "details": {},
            "raw_data": pd.DataFrame(),
        }

    def scan_multiple(self, symbols: list[str], period_days: int = 90) -> pd.DataFrame:
        """Scan multiple stocks and return sorted panic scores."""
        records = []
        for sym in symbols:
            result = self.compute_panic_score(sym, period_days)
            records.append({
                "Symbol": sym,
                "Panic Score": result["panic_score"],
                "Level": result["level"],
                **result["factors"],
            })

        df = pd.DataFrame(records)
        if not df.empty:
            df = df.sort_values("Panic Score", ascending=False).reset_index(drop=True)
        return df
