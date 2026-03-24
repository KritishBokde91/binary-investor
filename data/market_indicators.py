"""
Market-level indicators: breadth, sector performance, volatility proxy.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import streamlit as st

from config.settings import settings
from config.stock_universe import get_stocks_by_sector, get_all_sectors, get_sector_symbols
from data.stock_data import fetch_historical_data


@st.cache_data(ttl=settings.CACHE_TTL_REALTIME, show_spinner=False)
def compute_market_breadth(
    sector: str | None = None,
    period_days: int = 30,
) -> dict:
    """
    Compute advance-decline breadth for a sector or overall market.
    Returns: advancing, declining, unchanged, ad_ratio, breadth_signal.
    """
    if sector:
        symbols = get_sector_symbols(sector)
    else:
        # Sample across sectors
        symbols = []
        for sec in get_all_sectors()[:8]:
            symbols.extend(get_sector_symbols(sec)[:3])

    advancing = 0
    declining = 0
    unchanged = 0

    for sym in symbols:
        try:
            df = fetch_historical_data(sym, period_days)
            if df.empty or len(df) < 2:
                continue
            last_return = df["Returns"].iloc[-1]
            if last_return > 0.001:
                advancing += 1
            elif last_return < -0.001:
                declining += 1
            else:
                unchanged += 1
        except Exception:
            continue

    total = advancing + declining + unchanged
    ad_ratio = round(advancing / max(declining, 1), 2)

    if ad_ratio > 1.5:
        signal = "BULLISH"
    elif ad_ratio < 0.7:
        signal = "BEARISH"
    else:
        signal = "NEUTRAL"

    return {
        "advancing": advancing,
        "declining": declining,
        "unchanged": unchanged,
        "total": total,
        "ad_ratio": ad_ratio,
        "signal": signal,
    }


@st.cache_data(ttl=settings.CACHE_TTL_HISTORICAL, show_spinner=False)
def compute_sector_performance(period_days: int = 30) -> pd.DataFrame:
    """
    Compute sector-wise performance over given period.
    Returns DataFrame with: sector, avg_return, best_stock, worst_stock.
    """
    records = []
    for sector in get_all_sectors():
        symbols = get_sector_symbols(sector)
        if not symbols:
            continue

        returns = {}
        for sym in symbols[:5]:  # Top 5 per sector
            df = fetch_historical_data(sym, period_days)
            if not df.empty and len(df) > 1:
                total_return = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100
                returns[sym] = round(total_return, 2)

        if returns:
            avg_ret = round(np.mean(list(returns.values())), 2)
            best = max(returns, key=returns.get)
            worst = min(returns, key=returns.get)
            records.append({
                "Sector": sector,
                "Avg Return (%)": avg_ret,
                "Best Stock": best,
                "Best Return (%)": returns[best],
                "Worst Stock": worst,
                "Worst Return (%)": returns[worst],
                "Stocks Analyzed": len(returns),
            })

    return pd.DataFrame(records).sort_values("Avg Return (%)", ascending=False).reset_index(drop=True)


@st.cache_data(ttl=settings.CACHE_TTL_REALTIME, show_spinner=False)
def compute_volatility_regime(symbol: str = "^NSEI", period_days: int = 90) -> dict:
    """
    Estimate volatility regime using NIFTY rolling volatility as a VIX proxy.
    """
    df = fetch_historical_data(symbol, period_days)
    if df.empty or len(df) < 21:
        return {"current_vol": 0, "avg_vol": 0, "regime": "UNKNOWN", "percentile": 0}

    df["vol_20"] = df["Returns"].rolling(20).std() * np.sqrt(252) * 100

    current_vol = round(df["vol_20"].iloc[-1], 2)
    avg_vol = round(df["vol_20"].mean(), 2)
    percentile = round(
        (df["vol_20"] <= current_vol).sum() / len(df["vol_20"]) * 100, 1
    )

    if current_vol > avg_vol * 1.5:
        regime = "HIGH VOLATILITY"
    elif current_vol < avg_vol * 0.7:
        regime = "LOW VOLATILITY"
    else:
        regime = "NORMAL"

    return {
        "current_vol": current_vol,
        "avg_vol": avg_vol,
        "regime": regime,
        "percentile": percentile,
        "series": df[["vol_20"]].dropna(),
    }
