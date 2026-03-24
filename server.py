"""
SheepOrSleep — FastAPI Backend Server
Exposes all analytics as REST API for the Next.js frontend.
"""

from __future__ import annotations

import os
import json
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional
from scipy import stats

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─── App ──────────────────────────────────────────────
app = FastAPI(title="SheepOrSleep API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ─── Stock Universe ───────────────────────────────────
STOCK_UNIVERSE = [
    {"symbol": "RELIANCE.NS",  "name": "Reliance Industries",        "sector": "Energy",            "index": "NIFTY 50"},
    {"symbol": "TCS.NS",       "name": "Tata Consultancy Services",  "sector": "IT",                "index": "NIFTY 50"},
    {"symbol": "HDFCBANK.NS",  "name": "HDFC Bank",                  "sector": "Banking",           "index": "NIFTY 50"},
    {"symbol": "INFY.NS",      "name": "Infosys",                    "sector": "IT",                "index": "NIFTY 50"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank",                 "sector": "Banking",           "index": "NIFTY 50"},
    {"symbol": "HINDUNILVR.NS","name": "Hindustan Unilever",         "sector": "FMCG",              "index": "NIFTY 50"},
    {"symbol": "ITC.NS",       "name": "ITC Limited",                "sector": "FMCG",              "index": "NIFTY 50"},
    {"symbol": "SBIN.NS",      "name": "State Bank of India",        "sector": "Banking",           "index": "NIFTY 50"},
    {"symbol": "BHARTIARTL.NS","name": "Bharti Airtel",              "sector": "Telecom",           "index": "NIFTY 50"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank",        "sector": "Banking",           "index": "NIFTY 50"},
    {"symbol": "LT.NS",        "name": "Larsen & Toubro",            "sector": "Capital Goods",     "index": "NIFTY 50"},
    {"symbol": "AXISBANK.NS",  "name": "Axis Bank",                  "sector": "Banking",           "index": "NIFTY 50"},
    {"symbol": "ASIANPAINT.NS","name": "Asian Paints",               "sector": "Consumer Durables", "index": "NIFTY 50"},
    {"symbol": "MARUTI.NS",    "name": "Maruti Suzuki",              "sector": "Automobile",        "index": "NIFTY 50"},
    {"symbol": "TITAN.NS",     "name": "Titan Company",              "sector": "Consumer Durables", "index": "NIFTY 50"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma",                 "sector": "Pharma",            "index": "NIFTY 50"},
    {"symbol": "BAJFINANCE.NS","name": "Bajaj Finance",              "sector": "Financial Services","index": "NIFTY 50"},
    {"symbol": "WIPRO.NS",     "name": "Wipro",                      "sector": "IT",                "index": "NIFTY 50"},
    {"symbol": "HCLTECH.NS",   "name": "HCL Technologies",          "sector": "IT",                "index": "NIFTY 50"},
    {"symbol": "ULTRACEMCO.NS","name": "UltraTech Cement",           "sector": "Cement",            "index": "NIFTY 50"},
    {"symbol": "TATAMOTORS.NS","name": "Tata Motors",                "sector": "Automobile",        "index": "NIFTY 50"},
    {"symbol": "NTPC.NS",      "name": "NTPC",                       "sector": "Power",             "index": "NIFTY 50"},
    {"symbol": "POWERGRID.NS", "name": "Power Grid Corp",            "sector": "Power",             "index": "NIFTY 50"},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel",                 "sector": "Metals",            "index": "NIFTY 50"},
    {"symbol": "ONGC.NS",      "name": "ONGC",                       "sector": "Energy",            "index": "NIFTY 50"},
    {"symbol": "M&M.NS",       "name": "Mahindra & Mahindra",        "sector": "Automobile",        "index": "NIFTY 50"},
    {"symbol": "ADANIENT.NS",  "name": "Adani Enterprises",          "sector": "Conglomerate",      "index": "NIFTY 50"},
    {"symbol": "ADANIPORTS.NS","name": "Adani Ports",                "sector": "Infrastructure",    "index": "NIFTY 50"},
    {"symbol": "COALINDIA.NS", "name": "Coal India",                 "sector": "Mining",            "index": "NIFTY 50"},
    {"symbol": "BAJAJFINSV.NS","name": "Bajaj Finserv",              "sector": "Financial Services","index": "NIFTY 50"},
    {"symbol": "JSWSTEEL.NS",  "name": "JSW Steel",                  "sector": "Metals",            "index": "NIFTY 50"},
    {"symbol": "TECHM.NS",     "name": "Tech Mahindra",              "sector": "IT",                "index": "NIFTY 50"},
    {"symbol": "LTIM.NS",      "name": "LTIMindtree",                "sector": "IT",                "index": "NIFTY 50"},
    {"symbol": "NESTLEIND.NS", "name": "Nestle India",               "sector": "FMCG",              "index": "NIFTY 50"},
    {"symbol": "INDUSINDBK.NS","name": "IndusInd Bank",              "sector": "Banking",           "index": "NIFTY 50"},
    {"symbol": "CIPLA.NS",     "name": "Cipla",                      "sector": "Pharma",            "index": "NIFTY 50"},
    {"symbol": "DRREDDY.NS",   "name": "Dr Reddy's Labs",            "sector": "Pharma",            "index": "NIFTY 50"},
    {"symbol": "DIVISLAB.NS",  "name": "Divi's Laboratories",        "sector": "Pharma",            "index": "NIFTY 50"},
    {"symbol": "EICHERMOT.NS", "name": "Eicher Motors",              "sector": "Automobile",        "index": "NIFTY 50"},
    {"symbol": "APOLLOHOSP.NS","name": "Apollo Hospitals",           "sector": "Healthcare",        "index": "NIFTY 50"},
    {"symbol": "SBILIFE.NS",   "name": "SBI Life Insurance",         "sector": "Insurance",         "index": "NIFTY 50"},
    {"symbol": "BRITANNIA.NS", "name": "Britannia Industries",       "sector": "FMCG",              "index": "NIFTY 50"},
    {"symbol": "GRASIM.NS",    "name": "Grasim Industries",          "sector": "Cement",            "index": "NIFTY 50"},
    {"symbol": "BAJAJ-AUTO.NS","name": "Bajaj Auto",                 "sector": "Automobile",        "index": "NIFTY 50"},
    {"symbol": "HEROMOTOCO.NS","name": "Hero MotoCorp",              "sector": "Automobile",        "index": "NIFTY 50"},
    {"symbol": "TATACONSUM.NS","name": "Tata Consumer Products",     "sector": "FMCG",              "index": "NIFTY 50"},
    {"symbol": "HINDALCO.NS",  "name": "Hindalco Industries",        "sector": "Metals",            "index": "NIFTY 50"},
    {"symbol": "BPCL.NS",      "name": "BPCL",                       "sector": "Energy",            "index": "NIFTY 50"},
    {"symbol": "HDFCLIFE.NS",  "name": "HDFC Life Insurance",        "sector": "Insurance",         "index": "NIFTY 50"},
    {"symbol": "HAVELLS.NS",   "name": "Havells India",              "sector": "Consumer Durables", "index": "NIFTY NEXT 50"},
    {"symbol": "PIDILITIND.NS","name": "Pidilite Industries",        "sector": "Chemicals",         "index": "NIFTY NEXT 50"},
    {"symbol": "DABUR.NS",     "name": "Dabur India",                "sector": "FMCG",              "index": "NIFTY NEXT 50"},
    {"symbol": "GODREJCP.NS",  "name": "Godrej Consumer Products",   "sector": "FMCG",              "index": "NIFTY NEXT 50"},
    {"symbol": "SIEMENS.NS",   "name": "Siemens",                    "sector": "Capital Goods",     "index": "NIFTY NEXT 50"},
    {"symbol": "BANKBARODA.NS","name": "Bank of Baroda",             "sector": "Banking",           "index": "NIFTY NEXT 50"},
    {"symbol": "PNB.NS",       "name": "Punjab National Bank",       "sector": "Banking",           "index": "NIFTY NEXT 50"},
    {"symbol": "IOC.NS",       "name": "Indian Oil Corp",            "sector": "Energy",            "index": "NIFTY NEXT 50"},
    {"symbol": "DLF.NS",       "name": "DLF",                        "sector": "Real Estate",       "index": "NIFTY NEXT 50"},
    {"symbol": "TRENT.NS",     "name": "Trent Limited",              "sector": "Retail",            "index": "NIFTY NEXT 50"},
    {"symbol": "ZOMATO.NS",    "name": "Zomato",                     "sector": "Internet",          "index": "NIFTY NEXT 50"},
    {"symbol": "IRCTC.NS",     "name": "IRCTC",                      "sector": "Travel",            "index": "NIFTY NEXT 50"},
    {"symbol": "POLYCAB.NS",   "name": "Polycab India",              "sector": "Capital Goods",     "index": "NIFTY NEXT 50"},
    {"symbol": "JINDALSTEL.NS","name": "Jindal Steel & Power",       "sector": "Metals",            "index": "NIFTY NEXT 50"},
    {"symbol": "VEDL.NS",      "name": "Vedanta",                    "sector": "Metals",            "index": "NIFTY NEXT 50"},
    {"symbol": "TATAPOWER.NS", "name": "Tata Power",                 "sector": "Power",             "index": "NIFTY NEXT 50"},
    {"symbol": "HAL.NS",       "name": "Hindustan Aeronautics",      "sector": "Defence",           "index": "NIFTY NEXT 50"},
    {"symbol": "BEL.NS",       "name": "Bharat Electronics",         "sector": "Defence",           "index": "NIFTY NEXT 50"},
    {"symbol": "CHOLAFIN.NS",  "name": "Cholamandalam Finance",      "sector": "Financial Services","index": "NIFTY NEXT 50"},
    {"symbol": "MUTHOOTFIN.NS","name": "Muthoot Finance",            "sector": "Financial Services","index": "NIFTY NEXT 50"},
    {"symbol": "CANBK.NS",     "name": "Canara Bank",                "sector": "Banking",           "index": "NIFTY NEXT 50"},
    {"symbol": "MARICO.NS",    "name": "Marico",                     "sector": "FMCG",              "index": "NIFTY NEXT 50"},
    {"symbol": "LUPIN.NS",     "name": "Lupin",                      "sector": "Pharma",            "index": "NIFTY NEXT 50"},
    {"symbol": "TORNTPHARM.NS","name": "Torrent Pharma",             "sector": "Pharma",            "index": "NIFTY NEXT 50"},
    {"symbol": "NAUKRI.NS",    "name": "Info Edge (Naukri)",          "sector": "Internet",          "index": "NIFTY NEXT 50"},
    {"symbol": "PERSISTENT.NS","name": "Persistent Systems",         "sector": "IT",                "index": "NIFTY NEXT 50"},
    {"symbol": "MPHASIS.NS",   "name": "Mphasis",                    "sector": "IT",                "index": "NIFTY NEXT 50"},
    {"symbol": "AMBUJACEM.NS", "name": "Ambuja Cements",             "sector": "Cement",            "index": "NIFTY NEXT 50"},
]


def get_sector_symbols(sector: str) -> list[str]:
    return [s["symbol"] for s in STOCK_UNIVERSE if s["sector"] == sector]


# ─── Data Fetch ───────────────────────────────────────
def fetch_historical(symbol: str, period_days: int = 365) -> pd.DataFrame:
    try:
        end = datetime.now()
        start = end - timedelta(days=period_days)
        t = yf.Ticker(symbol)
        df = t.history(start=start, end=end, interval="1d")
        if df.empty:
            return pd.DataFrame()
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df["Returns"] = df["Close"].pct_change()
        df.dropna(inplace=True)
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        return df
    except Exception:
        return pd.DataFrame()


def fetch_quote(symbol: str) -> dict:
    try:
        t = yf.Ticker(symbol)
        info = t.info
        price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev = info.get("previousClose", 0)
        return {
            "symbol": symbol,
            "name": info.get("shortName", symbol),
            "price": round(price, 2) if price else 0,
            "prevClose": round(prev, 2) if prev else 0,
            "change": round(price - prev, 2) if price and prev else 0,
            "changePct": round((price - prev) / max(prev, 0.01) * 100, 2) if price and prev else 0,
            "volume": info.get("volume", 0),
            "avgVolume": info.get("averageVolume", 0),
            "dayHigh": info.get("dayHigh", 0),
            "dayLow": info.get("dayLow", 0),
            "week52High": info.get("fiftyTwoWeekHigh", 0),
            "week52Low": info.get("fiftyTwoWeekLow", 0),
            "marketCap": info.get("marketCap", 0),
            "peRatio": info.get("trailingPE", 0) or 0,
            "sector": info.get("sector", "N/A"),
        }
    except Exception:
        return {"symbol": symbol, "name": symbol, "price": 0, "prevClose": 0,
                "change": 0, "changePct": 0, "volume": 0, "avgVolume": 0,
                "dayHigh": 0, "dayLow": 0, "week52High": 0, "week52Low": 0,
                "marketCap": 0, "peRatio": 0, "sector": "N/A"}


# ─── Analytics: Herding ──────────────────────────────
def compute_herding(symbol: str, period_days: int = 365) -> dict:
    stock_info = next((s for s in STOCK_UNIVERSE if s["symbol"] == symbol), None)
    if not stock_info:
        return {"herdingDetected": False, "intensity": 0, "gamma2": 0, "pValue": 1,
                "rSquared": 0, "csadData": [], "sector": "Unknown", "error": "Stock not found"}

    sector = stock_info["sector"]
    sector_symbols = get_sector_symbols(sector)
    if len(sector_symbols) < 3:
        return {"herdingDetected": False, "intensity": 0, "gamma2": 0, "pValue": 1,
                "rSquared": 0, "csadData": [], "sector": sector, "error": "Need ≥3 stocks in sector"}

    returns_dict = {}
    for sym in sector_symbols:
        df = fetch_historical(sym, period_days)
        if not df.empty and "Returns" in df.columns:
            returns_dict[sym] = df["Returns"]

    if len(returns_dict) < 3:
        return {"herdingDetected": False, "intensity": 0, "gamma2": 0, "pValue": 1,
                "rSquared": 0, "csadData": [], "sector": sector, "error": "Insufficient data"}

    returns_df = pd.DataFrame(returns_dict).dropna()
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
        r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        n, k = len(y), 3
        mse = ss_res / (n - k)
        try:
            cov = mse * np.linalg.inv(X.T @ X)
            se = np.sqrt(np.diag(cov))
        except Exception:
            se = np.array([0, 0, 0])
        t_stat = gamma2 / se[2] if se[2] > 0 else 0
        p_val = 2 * (1 - stats.t.cdf(abs(t_stat), df=n - k))
        herding = gamma2 < 0 and p_val < 0.05
        intensity = min(100, abs(gamma2 / max(abs(gamma1), 1e-6)) * 100) if herding else max(0, min(20, abs(gamma2) * 1000))

        # build scatter data for chart (sample 200 points max)
        indices = np.linspace(0, len(abs_mkt) - 1, min(200, len(abs_mkt)), dtype=int)
        csad_data = [
            {"absReturn": round(float(abs_mkt.iloc[i]), 6),
             "csad": round(float(csad.iloc[i]), 6),
             "mktReturn": round(float(market_return.iloc[i]), 6),
             "fitted": round(float(y_pred[i]), 6)}
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
        return {"herdingDetected": False, "intensity": 0, "gamma2": 0, "pValue": 1,
                "rSquared": 0, "csadData": [], "sector": sector, "error": str(e)}


# ─── Analytics: Panic ─────────────────────────────────
def compute_panic(symbol: str, period_days: int = 90) -> dict:
    df = fetch_historical(symbol, period_days)
    if df.empty or len(df) < 21:
        return {"panicScore": 0, "level": "NO DATA", "factors": {}, "volumeData": []}

    # Technical indicators
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["Vol_SMA_20"] = df["Volume"].rolling(20).mean()
    df["Vol_Zscore"] = (df["Volume"] - df["Vol_SMA_20"]) / df["Volume"].rolling(20).std().replace(0, np.nan)
    df["Volatility"] = df["Returns"].rolling(20).std() * np.sqrt(252) * 100

    # Factor 1: Volume anomalies
    panic_vol = ((df["Vol_Zscore"] > 2) & (df["Returns"] < -0.005)).sum()
    score_vol = min(100, float(panic_vol) / max(len(df), 1) * 500)

    # Factor 2: Delivery pressure proxy
    df["Range"] = (df["High"] - df["Low"]) / df["Close"] * 100
    avg_range = df["Range"].rolling(20).mean()
    spec = (df["Range"] / avg_range.replace(0, np.nan)).clip(0, 5)
    est_del = np.clip(100 - spec * 20, 10, 90)
    low_del = (est_del < 30).sum()
    score_del = min(100, float(low_del) / max(len(df), 1) * 200)

    # Factor 3: Price-volume divergence
    price_mom = df["Close"].pct_change(5)
    vol_mom = df["Volume"].pct_change(5)
    div_count = ((price_mom < -0.03) & (vol_mom > 0.3)).sum()
    score_div = min(100, float(div_count) / max(len(df), 1) * 500)

    # Factor 4: Drawdown
    peak = df["Close"].expanding().max()
    dd = (df["Close"] / peak - 1) * 100
    current_dd = abs(float(dd.iloc[-1]))
    score_dd = min(100, current_dd * 5)

    # Factor 5: Volatility
    current_vol = float(df["Volatility"].dropna().iloc[-1]) if not df["Volatility"].dropna().empty else 0
    avg_vol = float(df["Volatility"].dropna().mean()) if not df["Volatility"].dropna().empty else 1
    score_vola = min(100, max(0, (current_vol / max(avg_vol, 1) - 1) * 100))

    panic_score = round(score_vol * 0.30 + score_del * 0.20 + score_div * 0.25 +
                        score_dd * 0.15 + score_vola * 0.10, 1)
    panic_score = min(100, max(0, panic_score))

    if panic_score >= 70: level = "EXTREME PANIC"
    elif panic_score >= 50: level = "HIGH PANIC"
    elif panic_score >= 30: level = "MODERATE"
    elif panic_score >= 10: level = "LOW"
    else: level = "CALM"

    # volume chart data (last 60 points)
    vol_df = df.tail(60)
    volume_data = [
        {"date": d.strftime("%b %d"),
         "volume": int(row["Volume"]),
         "zscore": round(float(row["Vol_Zscore"]), 2) if pd.notna(row["Vol_Zscore"]) else 0,
         "returns": round(float(row["Returns"]) * 100, 2),
         "isPanic": bool(row["Vol_Zscore"] > 2 and row["Returns"] < -0.005) if pd.notna(row["Vol_Zscore"]) else False}
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


# ─── Analytics: Behavior Gap ─────────────────────────
def compute_behavior_gap(symbol: str, period_years: int = 5) -> dict:
    df = fetch_historical(symbol, period_years * 365)
    if df.empty or len(df) < 100:
        return {"investmentCagr": 0, "investorCagr": 0, "behaviorGap": 0, "gapInterpretation": "Insufficient data"}

    bh_return = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100
    n_years = len(df) / 252
    bh_cagr = ((df["Close"].iloc[-1] / df["Close"].iloc[0]) ** (1 / max(n_years, 0.5)) - 1) * 100

    vol_normalized = df["Volume"] / df["Volume"].mean()
    price_normalized = (df["Close"] - df["Close"].min()) / (df["Close"].max() - df["Close"].min())
    corr = float(vol_normalized.corr(price_normalized))
    gap = max(0, corr * bh_cagr * 0.4)
    investor_cagr = bh_cagr - gap

    if gap > 3: interp = "Large gap — investors are buying high and selling low"
    elif gap > 1: interp = "Moderate gap — some emotional trading detected"
    else: interp = "Small gap — relatively rational trading behavior"

    return {
        "investmentReturn": round(bh_return, 2),
        "investmentCagr": round(bh_cagr, 2),
        "investorCagr": round(investor_cagr, 2),
        "behaviorGap": round(gap, 2),
        "periodYears": round(n_years, 1),
        "gapInterpretation": interp,
    }


def compute_missing_days(symbol: str, period_years: int = 10, initial: float = 100000) -> list[dict]:
    df = fetch_historical(symbol, period_years * 365)
    if df.empty or len(df) < 100:
        return []
    daily_returns = df["Returns"].values
    scenarios = [0, 5, 10, 15, 20, 30]
    results = []
    for miss_n in scenarios:
        modified = daily_returns.copy()
        if miss_n > 0:
            top = np.argsort(daily_returns)[::-1][:miss_n]
            for idx in top:
                modified[idx] = 0
        final = initial * np.prod(1 + modified)
        total_ret = (final / initial - 1) * 100
        cagr = ((final / initial) ** (365 / len(daily_returns)) - 1) * 100
        bh_final = initial * np.prod(1 + daily_returns) if miss_n > 0 else final
        results.append({
            "scenario": f"Missing {miss_n} best days" if miss_n > 0 else "Fully invested",
            "finalValue": round(float(final), 0),
            "totalReturn": round(float(total_ret), 1),
            "cagr": round(float(cagr), 2),
            "reduction": round(float((bh_final - final) / bh_final * 100), 1) if miss_n > 0 else 0,
        })
    return results


# ─── Analytics: Monte Carlo ───────────────────────────
def simulate_sip_vs_panic(symbol: str, years: int = 10, sip: float = 10000, n_sims: int = 500) -> dict:
    df = fetch_historical(symbol, min(years, 5) * 365)
    if df.empty or len(df) < 50:
        mean_r, std_r = 0.0005, 0.015
    else:
        mean_r = float(df["Returns"].mean())
        std_r = float(df["Returns"].std())

    trading_days = 252 * years
    monthly = 21
    sip_results, panic_results = [], []

    for _ in range(n_sims):
        sim = np.random.normal(mean_r, std_r, trading_days)
        # SIP
        units, price = 0.0, 100.0
        for d in range(trading_days):
            price *= (1 + sim[d]); price = max(price, 0.01)
            if d % monthly == 0: units += sip / price
        sip_results.append(units * price)
        # Panic
        units, cash, price, peak = 0.0, 0.0, 100.0, 100.0
        in_mkt, wait = True, 0
        for d in range(trading_days):
            price *= (1 + sim[d]); price = max(price, 0.01)
            if in_mkt:
                peak = max(peak, price)
                if (price - peak) / peak <= -0.10:
                    cash += units * price; units = 0; in_mkt = False; wait = 90
                if d % monthly == 0: units += sip / price
            else:
                wait -= 1
                if d % monthly == 0: cash += sip
                if wait <= 0:
                    in_mkt = True; peak = price; units += cash / price; cash = 0
        panic_results.append(units * price + cash)

    sip_arr, panic_arr = np.array(sip_results), np.array(panic_results)
    total_invested = sip * (trading_days // monthly)

    # build histogram data
    all_vals = np.concatenate([sip_arr, panic_arr])
    bin_min, bin_max = float(np.min(all_vals)), float(np.max(all_vals))
    n_bins = 30
    bin_edges = np.linspace(bin_min, bin_max, n_bins + 1)
    sip_hist, _ = np.histogram(sip_arr, bins=bin_edges)
    panic_hist, _ = np.histogram(panic_arr, bins=bin_edges)
    histogram = [
        {"binStart": round(float(bin_edges[i]), 0),
         "binEnd": round(float(bin_edges[i + 1]), 0),
         "sip": int(sip_hist[i]),
         "panic": int(panic_hist[i])}
        for i in range(n_bins)
    ]

    return {
        "totalInvested": round(float(total_invested), 0),
        "years": years,
        "nSimulations": n_sims,
        "sip": {
            "mean": round(float(np.mean(sip_arr)), 0),
            "median": round(float(np.median(sip_arr)), 0),
            "p10": round(float(np.percentile(sip_arr, 10)), 0),
            "p90": round(float(np.percentile(sip_arr, 90)), 0),
        },
        "panic": {
            "mean": round(float(np.mean(panic_arr)), 0),
            "median": round(float(np.median(panic_arr)), 0),
            "p10": round(float(np.percentile(panic_arr, 10)), 0),
            "p90": round(float(np.percentile(panic_arr, 90)), 0),
        },
        "costOfPanic": {
            "meanLoss": round(float(np.mean(sip_arr) - np.mean(panic_arr)), 0),
            "pctLoss": round(float((np.mean(sip_arr) - np.mean(panic_arr)) / max(np.mean(sip_arr), 1) * 100), 1),
            "winRate": round(float((sip_arr > panic_arr).sum() / len(sip_arr) * 100), 1),
        },
        "histogram": histogram,
    }


# ─── Analytics: Price chart ───────────────────────────
def get_price_chart(symbol: str, period_days: int = 365) -> list[dict]:
    df = fetch_historical(symbol, period_days)
    if df.empty:
        return []
    # sample to ~120 points
    step = max(1, len(df) // 120)
    sampled = df.iloc[::step]
    return [
        {"date": d.strftime("%b %d, %Y"),
         "open": round(float(row["Open"]), 2),
         "high": round(float(row["High"]), 2),
         "low": round(float(row["Low"]), 2),
         "close": round(float(row["Close"]), 2),
         "volume": int(row["Volume"])}
        for d, row in sampled.iterrows()
    ]


# ─── API Routes ──────────────────────────────────────

@app.get("/api/stocks")
def list_stocks():
    return {"stocks": STOCK_UNIVERSE}


@app.get("/api/quote")
def get_quote(symbol: str):
    return fetch_quote(symbol)


class AnalyzeRequest(BaseModel):
    symbol: str
    periodDays: int = 365
    sipAmount: float = 10000
    simYears: int = 10
    nSimulations: int = 500


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    """One-tap: run ALL analytics for a stock and return everything."""
    quote = fetch_quote(req.symbol)
    price_chart = get_price_chart(req.symbol, req.periodDays)
    herding = compute_herding(req.symbol, req.periodDays)
    panic = compute_panic(req.symbol, min(req.periodDays, 180))
    gap = compute_behavior_gap(req.symbol, max(req.periodDays // 365, 2))
    missing = compute_missing_days(req.symbol, max(req.periodDays // 365, 3))
    mc = simulate_sip_vs_panic(req.symbol, req.simYears, req.sipAmount, req.nSimulations)

    return {
        "quote": quote,
        "priceChart": price_chart,
        "herding": herding,
        "panic": panic,
        "behaviorGap": gap,
        "missingDays": missing,
        "monteCarlo": mc,
    }


class ChatRequest(BaseModel):
    messages: list[dict]
    context: str = ""


@app.post("/api/chat")
def chat(req: ChatRequest):
    if not GROQ_API_KEY:
        return {"response": "⚠️ Groq API key not configured. Please set GROQ_API_KEY in .env"}
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        system = """You are **SheepOrSleep AI**, an expert behavioral finance advisor for the Indian stock market.
Help retail investors overcome biases like herd mentality, panic selling, and loss aversion.
Always use ₹ (INR). Never give specific buy/sell recommendations. Encourage SIP discipline.
Keep responses concise with clear formatting."""
        if req.context:
            system += f"\n\nCurrent context:\n{req.context}"

        messages = [{"role": "system", "content": system}] + req.messages
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"response": f"⚠️ Error: {e}"}


@app.get("/api/health")
def health():
    return {"status": "ok", "groq": bool(GROQ_API_KEY)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
