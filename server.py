"""
SheepOrSleep — FastAPI Backend Server
Exposes all analytics as REST API for the Next.js frontend.
"""

from __future__ import annotations

import os
import sys
import re
import json
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone, timedelta
from typing import Optional, Literal
from scipy import stats

# Ensure src is on sys.path
_SRC_DIR = str(Path(__file__).resolve().parent / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from sheep_or_sleep.analytics import (
    compute_behavior_gap as compute_behavior_gap_analytics,
    compute_missing_days as compute_missing_days_analytics,
    compute_cck_herding,
    compute_panic_score,
    simulate_sip_vs_panic as simulate_sip_vs_panic_analytics,
)

from dotenv import load_dotenv
load_dotenv()

import asyncio
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from sheep_or_sleep.cache.service import CacheService
from sheep_or_sleep.api.auth import get_auth_user
from sheep_or_sleep.api.rate_limiter import check_rate_limit
from sheep_or_sleep.api.schemas import (
    LivenessResponse,
    ReadinessResponse,
    MetricsResponse,
    StockListResponse,
    QuoteResponse,
    AnalyzeResponse,
    ChatResponse,
    HealthResponse,
)

# ─── App ──────────────────────────────────────────────
app = FastAPI(title="SheepOrSleep API", version="1.0.0")
cache_service = CacheService()

raw_origins = os.getenv("ALLOWED_ORIGINS", os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"))
allowed_origins = [orig.strip() for orig in raw_origins.split(",") if orig.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
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

KNOWN_SYMBOLS = {s["symbol"] for s in STOCK_UNIVERSE}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9&.-]{1,20}$")


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
        return {
            "herdingDetected": False,
            "intensity": 0.0,
            "gamma2": 0.0,
            "pValue": 1.0,
            "rSquared": 0.0,
            "csadData": [],
            "sector": "Unknown",
            "error": "Stock not found",
        }

    sector = stock_info["sector"]
    sector_symbols = get_sector_symbols(sector)
    returns_dict = {}
    for sym in sector_symbols:
        df = fetch_historical(sym, period_days)
        if not df.empty and "Returns" in df.columns:
            returns_dict[sym] = df["Returns"]

    return compute_cck_herding(returns_dict, sector=sector)


# ─── Analytics: Panic ─────────────────────────────────
def compute_panic(symbol: str, period_days: int = 90) -> dict:
    df = fetch_historical(symbol, period_days)
    return compute_panic_score(df)


# ─── Analytics: Behavior Gap ─────────────────────────
def compute_behavior_gap(symbol: str, period_years: int = 5) -> dict:
    df = fetch_historical(symbol, period_years * 365)
    return compute_behavior_gap_analytics(df)


def compute_missing_days(symbol: str, period_years: int = 10, initial: float = 100000.0) -> list[dict]:
    df = fetch_historical(symbol, period_years * 365)
    return compute_missing_days_analytics(df, initial=initial)


# ─── Analytics: Monte Carlo ───────────────────────────
def simulate_sip_vs_panic(symbol: str, years: int = 10, sip: float = 10000.0, n_sims: int = 500) -> dict:
    df = fetch_historical(symbol, min(years, 5) * 365)
    if df.empty or len(df) < 50:
        mean_r, std_r = 0.0005, 0.015
    else:
        mean_r = float(df["Returns"].mean())
        std_r = float(df["Returns"].std())
    return simulate_sip_vs_panic_analytics(
        mean_r=mean_r,
        std_r=std_r,
        years=years,
        sip=sip,
        n_sims=n_sims,
    )


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


# ─── System Readiness ─────────────────────────────────

async def check_system_readiness() -> dict[str, str]:
    pg_status = "ok"
    redis_status = "ok"

    # Check Postgres
    try:
        from sheep_or_sleep.db.base import get_async_engine
        from sqlalchemy import text
        engine = get_async_engine()
        async with engine.connect() as conn:
            await asyncio.wait_for(conn.execute(text("SELECT 1")), timeout=2.0)
    except Exception:
        pg_status = "down"

    # Check Redis
    try:
        from sheep_or_sleep.cache.client import get_redis_client
        redis_client = get_redis_client()
        await asyncio.wait_for(redis_client.ping(), timeout=2.0)
    except Exception:
        redis_status = "down"

    overall = "ok" if (pg_status == "ok" and redis_status == "ok") else "down"
    return {
        "status": overall,
        "postgres": pg_status,
        "redis": redis_status,
    }


# ─── Probes & Observability ───────────────────────────

@app.get("/healthz", response_model=LivenessResponse)
async def healthz():
    return {"status": "ok"}


@app.get("/readyz", response_model=ReadinessResponse)
async def readyz():
    res = await check_system_readiness()
    if res["status"] != "ok":
        raise HTTPException(status_code=503, detail=res)
    return res


@app.get("/api/metrics", response_model=MetricsResponse)
async def api_metrics():
    return await cache_service.get_metrics()


# ─── API Routes ──────────────────────────────────────

@app.get("/api/stocks", response_model=StockListResponse)
async def list_stocks():
    return {"stocks": STOCK_UNIVERSE}


@app.get("/api/quote", response_model=QuoteResponse)
async def get_quote(
    symbol: str,
    auth: str = Depends(get_auth_user),
    _rate: None = Depends(check_rate_limit),
):
    if not SYMBOL_PATTERN.match(symbol) or symbol not in KNOWN_SYMBOLS:
        raise HTTPException(status_code=400, detail=f"Invalid or unknown symbol: {symbol}")

    async def _fetch():
        return fetch_quote(symbol)

    cached_quote = await cache_service.get_or_compute(
        f"quote:{symbol}",
        _fetch,
        ttl_sec=60,
        stale_ttl_sec=300,
    )
    return cached_quote


class AnalyzeRequest(BaseModel):
    symbol: str
    periodDays: int = Field(365, ge=90, le=3650)
    sipAmount: float = Field(10000, gt=0, le=1000000)
    simYears: int = Field(10, ge=1, le=30)
    nSimulations: int = Field(500, ge=100, le=20000)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        if not SYMBOL_PATTERN.match(v):
            raise ValueError(f"Invalid symbol format: {v}")
        if v not in KNOWN_SYMBOLS:
            raise ValueError(f"Unknown symbol: {v}. Must be in supported stock universe.")
        return v


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(
    req: AnalyzeRequest,
    auth: str = Depends(get_auth_user),
    _rate: None = Depends(check_rate_limit),
):
    """One-tap: run ALL analytics for a stock and return everything."""
    # Pre-check historical data and quote to avoid silent zero-filled responses
    hist_check = fetch_historical(req.symbol, req.periodDays)
    quote = fetch_quote(req.symbol)
    if hist_check.empty or quote.get("price", 0) <= 0:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unavailable",
                "as_of": datetime.now(timezone.utc).isoformat(),
                "reason": f"Market data upstream unavailable for symbol {req.symbol}",
            },
        )

    async def _compute_all():
        price_chart = get_price_chart(req.symbol, req.periodDays)
        herding = compute_herding(req.symbol, req.periodDays)
        panic = compute_panic(req.symbol, min(req.periodDays, 180))
        gap = compute_behavior_gap(req.symbol, max(req.periodDays // 365, 2))
        missing = compute_missing_days(req.symbol, max(req.periodDays // 365, 3))
        mc = simulate_sip_vs_panic(req.symbol, req.simYears, req.sipAmount, req.nSimulations)

        status: Literal["ok", "degraded", "unavailable"] = "ok"
        reasons: list[str] = []

        if herding.get("error"):
            status = "degraded"
            reasons.append(f"Herding: {herding['error']}")
        if panic.get("level") == "NO DATA":
            status = "degraded"
            reasons.append("Panic: Insufficient data")
        if gap.get("gapInterpretation") == "Insufficient data":
            status = "degraded"
            reasons.append("BehaviorGap: Insufficient data")

        return {
            "status": status,
            "as_of": datetime.now(timezone.utc).isoformat(),
            "data_version": "1.0",
            "reason": "; ".join(reasons) if reasons else None,
            "quote": quote,
            "priceChart": price_chart,
            "herding": herding,
            "panic": panic,
            "behaviorGap": gap,
            "missingDays": missing,
            "monteCarlo": mc,
        }

    cache_key = f"analysis:{req.symbol}:{req.periodDays}:{req.sipAmount}:{req.simYears}:{req.nSimulations}"
    return await cache_service.get_or_compute(cache_key, _compute_all, ttl_sec=300, stale_ttl_sec=1800)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=2000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., max_length=50)
    context: Optional[str] = None  # Dropped from system prompt per AUDIT.md Phase 0 Item f


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    auth: str = Depends(get_auth_user),
    _rate: None = Depends(check_rate_limit),
):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=503, detail="Groq API key not configured.")
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        system = """You are **SheepOrSleep AI**, an expert behavioral finance advisor for the Indian stock market.
Help retail investors overcome biases like herd mentality, panic selling, and loss aversion.
Always use ₹ (INR). Never give specific buy/sell recommendations. Encourage SIP discipline.
Keep responses concise with clear formatting."""

        messages = [{"role": "system", "content": system}] + [
            {"role": m.role, "content": m.content} for m in req.messages
        ]
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
        )
        return {"response": response.choices[0].message.content}
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the chat request.",
        )


@app.get("/api/health", response_model=HealthResponse)
async def health():
    return {"status": "ok", "groq": bool(GROQ_API_KEY)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
