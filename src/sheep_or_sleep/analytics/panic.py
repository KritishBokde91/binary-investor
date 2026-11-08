"""
Multi-factor Panic Selling Score Analytics.
Factors:
1. Volume Anomaly (30%): Lagged volume z-score > 2 on down-days
2. Intraday Range Ratio (20%): Range expansion relative to 20-day mean
3. Price-Volume Divergence (25%): Price drop with volume surge
4. Drawdown Severity (15%): Drawdown from high of analysis window
5. Volatility Regime (10%): Realized vs average volatility
"""

from __future__ import annotations
import numpy as np
import pandas as pd


def compute_panic_score(df: pd.DataFrame) -> dict:
    """
    Compute 5-factor panic score (0-100) using lagged volume window.
    """
    if df.empty or len(df) < 21:
        return {"panicScore": 0, "level": "NO DATA", "factors": {}, "volumeData": []}

    df = df.copy()

    # Technical indicators
    df["SMA_20"] = df["Close"].rolling(20).mean()
    # Lagged volume baseline (excludes today to prevent saturation)
    vol_mean_20 = df["Volume"].shift(1).rolling(20).mean()
    vol_std_20 = df["Volume"].shift(1).rolling(20).std().replace(0, np.nan)
    df["Vol_SMA_20"] = vol_mean_20
    df["Vol_Zscore"] = (df["Volume"] - vol_mean_20) / vol_std_20
    df["Volatility"] = df["Returns"].rolling(20).std() * np.sqrt(252) * 100

    # Factor 1: Volume anomalies
    panic_vol = ((df["Vol_Zscore"] > 2) & (df["Returns"] < -0.005)).sum()
    score_vol = min(100.0, float(panic_vol) / max(len(df), 1) * 500)

    # Factor 2: Delivery / range proxy
    df["Range"] = (df["High"] - df["Low"]) / df["Close"] * 100
    avg_range = df["Range"].rolling(20).mean()
    spec = (df["Range"] / avg_range.replace(0, np.nan)).clip(0, 5)
    est_del = np.clip(100 - spec * 20, 10, 90)
    low_del = (est_del < 30).sum()
    score_del = min(100.0, float(low_del) / max(len(df), 1) * 200)

    # Factor 3: Price-volume divergence
    price_mom = df["Close"].pct_change(5)
    vol_mom = df["Volume"].pct_change(5)
    div_count = ((price_mom < -0.03) & (vol_mom > 0.3)).sum()
    score_div = min(100.0, float(div_count) / max(len(df), 1) * 500)

    # Factor 4: Drawdown from window peak
    peak = df["Close"].expanding().max()
    dd = (df["Close"] / peak - 1) * 100
    current_dd = abs(float(dd.iloc[-1])) if not dd.empty else 0.0
    score_dd = min(100.0, current_dd * 5)

    # Factor 5: Volatility
    valid_vol = df["Volatility"].dropna()
    current_vol = float(valid_vol.iloc[-1]) if not valid_vol.empty else 0.0
    avg_vol = float(valid_vol.mean()) if not valid_vol.empty else 1.0
    score_vola = min(100.0, max(0.0, (current_vol / max(avg_vol, 1.0) - 1) * 100))

    panic_score = round(
        score_vol * 0.30 + score_del * 0.20 + score_div * 0.25 + score_dd * 0.15 + score_vola * 0.10,
        1,
    )
    panic_score = min(100.0, max(0.0, panic_score))

    if panic_score >= 70:
        level = "EXTREME PANIC"
    elif panic_score >= 50:
        level = "HIGH PANIC"
    elif panic_score >= 30:
        level = "MODERATE"
    elif panic_score >= 10:
        level = "LOW"
    else:
        level = "CALM"

    vol_df = df.tail(60)
    volume_data = [
        {
            "date": d.strftime("%b %d") if hasattr(d, "strftime") else str(d),
            "volume": int(row["Volume"]),
            "zscore": round(float(row["Vol_Zscore"]), 2) if pd.notna(row["Vol_Zscore"]) else 0,
            "returns": round(float(row["Returns"]) * 100, 2) if pd.notna(row["Returns"]) else 0,
            "isPanic": bool(row["Vol_Zscore"] > 2 and row["Returns"] < -0.005) if pd.notna(row["Vol_Zscore"]) else False,
        }
        for d, row in vol_df.iterrows()
    ]

    return {
        "panicScore": panic_score,
        "level": level,
        "factors": {
            "volumeAnomaly": round(score_vol, 1),
            "deliveryPressure": round(score_del, 1),
            "priceVolDivergence": round(score_div, 1),
            "drawdownSeverity": round(score_dd, 1),
            "volatilityRegime": round(score_vola, 1),
        },
        "details": {
            "currentDrawdown": round(current_dd, 2),
            "currentVolatility": round(current_vol, 2),
            "avgVolatility": round(avg_vol, 2),
        },
        "volumeData": volume_data,
    }
