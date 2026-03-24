"""
Dynamic Indian Stock Universe — Nifty 50, Nifty Next 50, sector leaders.
Users can search / filter / select any Indian stock dynamically.
"""

from __future__ import annotations

STOCK_UNIVERSE: list[dict] = [
    # ── NIFTY 50 ──────────────────────────────────────────────
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
    {"symbol": "BAJFINANCE.NS","name": "Bajaj Finance",              "sector": "Financial Services", "index": "NIFTY 50"},
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
    {"symbol": "BAJAJFINSV.NS","name": "Bajaj Finserv",              "sector": "Financial Services", "index": "NIFTY 50"},
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
    {"symbol": "WIPRO.NS",     "name": "Wipro",                      "sector": "IT",                "index": "NIFTY 50"},
    {"symbol": "HDFCLIFE.NS",  "name": "HDFC Life Insurance",        "sector": "Insurance",         "index": "NIFTY 50"},

    # ── NIFTY NEXT 50 / Midcap Leaders ────────────────────────
    {"symbol": "HAVELLS.NS",   "name": "Havells India",              "sector": "Consumer Durables",  "index": "NIFTY NEXT 50"},
    {"symbol": "PIDILITIND.NS","name": "Pidilite Industries",        "sector": "Chemicals",          "index": "NIFTY NEXT 50"},
    {"symbol": "DABUR.NS",     "name": "Dabur India",                "sector": "FMCG",               "index": "NIFTY NEXT 50"},
    {"symbol": "GODREJCP.NS",  "name": "Godrej Consumer Products",   "sector": "FMCG",               "index": "NIFTY NEXT 50"},
    {"symbol": "SIEMENS.NS",   "name": "Siemens",                    "sector": "Capital Goods",      "index": "NIFTY NEXT 50"},
    {"symbol": "BANKBARODA.NS","name": "Bank of Baroda",             "sector": "Banking",            "index": "NIFTY NEXT 50"},
    {"symbol": "PNB.NS",       "name": "Punjab National Bank",       "sector": "Banking",            "index": "NIFTY NEXT 50"},
    {"symbol": "IOC.NS",       "name": "Indian Oil Corp",            "sector": "Energy",             "index": "NIFTY NEXT 50"},
    {"symbol": "DLF.NS",       "name": "DLF",                        "sector": "Real Estate",        "index": "NIFTY NEXT 50"},
    {"symbol": "TRENT.NS",     "name": "Trent Limited",              "sector": "Retail",             "index": "NIFTY NEXT 50"},
    {"symbol": "ZOMATO.NS",    "name": "Zomato",                     "sector": "Internet",           "index": "NIFTY NEXT 50"},
    {"symbol": "IRCTC.NS",     "name": "IRCTC",                      "sector": "Travel",             "index": "NIFTY NEXT 50"},
    {"symbol": "POLYCAB.NS",   "name": "Polycab India",              "sector": "Capital Goods",      "index": "NIFTY NEXT 50"},
    {"symbol": "JINDALSTEL.NS","name": "Jindal Steel & Power",       "sector": "Metals",             "index": "NIFTY NEXT 50"},
    {"symbol": "VEDL.NS",      "name": "Vedanta",                    "sector": "Metals",             "index": "NIFTY NEXT 50"},
    {"symbol": "TATAPOWER.NS", "name": "Tata Power",                 "sector": "Power",              "index": "NIFTY NEXT 50"},
    {"symbol": "HAL.NS",       "name": "Hindustan Aeronautics",      "sector": "Defence",            "index": "NIFTY NEXT 50"},
    {"symbol": "BEL.NS",       "name": "Bharat Electronics",         "sector": "Defence",            "index": "NIFTY NEXT 50"},
    {"symbol": "CHOLAFIN.NS",  "name": "Cholamandalam Finance",      "sector": "Financial Services",  "index": "NIFTY NEXT 50"},
    {"symbol": "MUTHOOTFIN.NS","name": "Muthoot Finance",            "sector": "Financial Services",  "index": "NIFTY NEXT 50"},
    {"symbol": "CANBK.NS",     "name": "Canara Bank",                "sector": "Banking",            "index": "NIFTY NEXT 50"},
    {"symbol": "MARICO.NS",    "name": "Marico",                     "sector": "FMCG",               "index": "NIFTY NEXT 50"},
    {"symbol": "PAGEIND.NS",   "name": "Page Industries",            "sector": "Textiles",           "index": "NIFTY NEXT 50"},
    {"symbol": "LUPIN.NS",     "name": "Lupin",                      "sector": "Pharma",             "index": "NIFTY NEXT 50"},
    {"symbol": "TORNTPHARM.NS","name": "Torrent Pharma",             "sector": "Pharma",             "index": "NIFTY NEXT 50"},
    {"symbol": "ICICIPRULI.NS","name": "ICICI Prudential Life",      "sector": "Insurance",          "index": "NIFTY NEXT 50"},
    {"symbol": "NAUKRI.NS",    "name": "Info Edge (Naukri)",          "sector": "Internet",           "index": "NIFTY NEXT 50"},
    {"symbol": "PERSISTENT.NS","name": "Persistent Systems",         "sector": "IT",                 "index": "NIFTY NEXT 50"},
    {"symbol": "MPHASIS.NS",   "name": "Mphasis",                    "sector": "IT",                 "index": "NIFTY NEXT 50"},
    {"symbol": "AMBUJACEM.NS", "name": "Ambuja Cements",             "sector": "Cement",             "index": "NIFTY NEXT 50"},

    # ── INDEX TICKERS ─────────────────────────────────────────
    {"symbol": "^NSEI",        "name": "NIFTY 50",                   "sector": "Index",             "index": "Index"},
    {"symbol": "^BSESN",       "name": "SENSEX",                     "sector": "Index",             "index": "Index"},
    {"symbol": "^NSEBANK",     "name": "BANK NIFTY",                 "sector": "Index",             "index": "Index"},
]


def get_all_sectors() -> list[str]:
    """Return unique sectors sorted alphabetically."""
    sectors = sorted({s["sector"] for s in STOCK_UNIVERSE if s["sector"] != "Index"})
    return sectors


def get_stocks_by_sector(sector: str) -> list[dict]:
    """Filter stocks by sector."""
    return [s for s in STOCK_UNIVERSE if s["sector"] == sector]


def get_indices() -> list[dict]:
    """Return index tickers only."""
    return [s for s in STOCK_UNIVERSE if s["index"] == "Index"]


def search_stocks(query: str) -> list[dict]:
    """Fuzzy search stocks by name or symbol."""
    q = query.lower().strip()
    if not q:
        return [s for s in STOCK_UNIVERSE if s["index"] != "Index"]
    return [
        s for s in STOCK_UNIVERSE
        if q in s["name"].lower() or q in s["symbol"].lower()
    ]


def get_display_options() -> list[str]:
    """Return formatted display strings for selectbox (excludes indices)."""
    return [
        f"{s['name']}  ({s['symbol']})"
        for s in STOCK_UNIVERSE
        if s["index"] != "Index"
    ]


def symbol_from_display(display: str) -> str:
    """Extract symbol from display string like 'Reliance Industries  (RELIANCE.NS)'."""
    try:
        return display.split("(")[-1].rstrip(")")
    except Exception:
        return display


def get_sector_symbols(sector: str) -> list[str]:
    """Return list of ticker symbols for a sector."""
    return [s["symbol"] for s in STOCK_UNIVERSE if s["sector"] == sector and s["index"] != "Index"]
