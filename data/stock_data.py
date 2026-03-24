"""
Stock data acquisition via yfinance — historical OHLCV, real-time quotes, sector data.
All functions are Streamlit-cache-friendly.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta

from config.settings import settings


@st.cache_data(ttl=settings.CACHE_TTL_HISTORICAL, show_spinner=False)
def fetch_historical_data(
    symbol: str,
    period_days: int = 365,
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a given NSE/BSE ticker.

    Returns DataFrame with columns: Open, High, Low, Close, Volume, Returns
    """
    try:
        end = datetime.now()
        start = end - timedelta(days=period_days)
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, interval=interval)

        if df.empty:
            return pd.DataFrame()

        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df["Returns"] = df["Close"].pct_change()
        df["Log_Returns"] = np.log(df["Close"] / df["Close"].shift(1))
        df.dropna(inplace=True)
        df.index = pd.to_datetime(df.index)
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        return df

    except Exception as e:
        st.warning(f"Could not fetch data for {symbol}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=settings.CACHE_TTL_REALTIME, show_spinner=False)
def fetch_realtime_quote(symbol: str) -> dict:
    """
    Fetch real-time quote for a ticker.

    Returns dict with: price, change, change_pct, volume, day_high, day_low,
    52w_high, 52w_low, market_cap, pe_ratio, name.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        return {
            "symbol": symbol,
            "name": info.get("shortName", symbol),
            "price": info.get("currentPrice") or info.get("regularMarketPrice", 0),
            "prev_close": info.get("previousClose", 0),
            "change": round(
                (info.get("currentPrice") or info.get("regularMarketPrice", 0))
                - info.get("previousClose", 0), 2
            ),
            "change_pct": round(
                (
                    (info.get("currentPrice") or info.get("regularMarketPrice", 0))
                    - info.get("previousClose", 0)
                )
                / max(info.get("previousClose", 1), 0.01) * 100, 2
            ),
            "volume": info.get("volume", 0),
            "avg_volume": info.get("averageVolume", 0),
            "day_high": info.get("dayHigh", 0),
            "day_low": info.get("dayLow", 0),
            "week_52_high": info.get("fiftyTwoWeekHigh", 0),
            "week_52_low": info.get("fiftyTwoWeekLow", 0),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
        }

    except Exception:
        return {
            "symbol": symbol, "name": symbol, "price": 0, "prev_close": 0,
            "change": 0, "change_pct": 0, "volume": 0, "avg_volume": 0,
            "day_high": 0, "day_low": 0, "week_52_high": 0, "week_52_low": 0,
            "market_cap": 0, "pe_ratio": 0, "sector": "N/A", "industry": "N/A",
        }


@st.cache_data(ttl=settings.CACHE_TTL_HISTORICAL, show_spinner=False)
def fetch_multi_stock_data(
    symbols: list[str],
    period_days: int = 365,
) -> dict[str, pd.DataFrame]:
    """Fetch historical data for multiple tickers (for cross-sectional analysis)."""
    result = {}
    for sym in symbols:
        df = fetch_historical_data(sym, period_days)
        if not df.empty:
            result[sym] = df
    return result


@st.cache_data(ttl=settings.CACHE_TTL_REALTIME, show_spinner=False)
def fetch_index_data() -> dict[str, dict]:
    """Fetch real-time quotes for major Indian indices."""
    indices = {"^NSEI": "NIFTY 50", "^BSESN": "SENSEX", "^NSEBANK": "BANK NIFTY"}
    result = {}
    for symbol, name in indices.items():
        quote = fetch_realtime_quote(symbol)
        quote["display_name"] = name
        result[symbol] = quote
    return result


def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add common technical indicators to OHLCV DataFrame."""
    if df.empty:
        return df

    df = df.copy()

    # Moving Averages
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_50"] = df["Close"].rolling(window=50).mean()
    df["SMA_200"] = df["Close"].rolling(window=200).mean()
    df["EMA_12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA_26"] = df["Close"].ewm(span=26, adjust=False).mean()

    # MACD
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # RSI (14-period)
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    df["BB_Mid"] = df["Close"].rolling(window=20).mean()
    bb_std = df["Close"].rolling(window=20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * bb_std
    df["BB_Lower"] = df["BB_Mid"] - 2 * bb_std

    # Volume metrics
    df["Volume_SMA_20"] = df["Volume"].rolling(window=20).mean()
    df["Volume_Ratio"] = df["Volume"] / df["Volume_SMA_20"].replace(0, np.nan)

    # Volatility
    df["Volatility_20"] = df["Returns"].rolling(window=20).std() * np.sqrt(252) * 100

    return df
