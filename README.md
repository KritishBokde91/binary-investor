<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.135-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq-LLaMA_3.3-F55036?style=for-the-badge&logo=meta&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

<h1 align="center">🐑 SheepOrSleep</h1>
<h3 align="center">AI-Powered Behavioral Bias Detector for Indian Stocks</h3>

<p align="center">
  <em>Are you following the herd — or sleeping through critical market shifts?</em>
  <br />
  One-tap behavioral analysis for any Indian stock with herding detection, panic scoring, Monte Carlo simulation, and Groq AI copilot.
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Analytics Deep Dive](#-analytics-deep-dive)
- [Frontend Components](#-frontend-components)
- [Environment Variables](#-environment-variables)
- [Screenshots](#-screenshots)
- [Research Background](#-research-background)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🧠 Overview

**SheepOrSleep** is a production-ready, full-stack behavioral finance application that helps Indian retail investors identify and overcome psychological biases — **herd mentality**, **panic selling**, and **emotional trading** — using econometric models and AI.

The application combines:

- **Econometric analysis** using the CCK (Chang, Cheng & Khorana) herding detection model
- **Multi-factor panic scoring** with volume anomaly detection
- **Monte Carlo simulations** comparing disciplined SIP vs panic-selling outcomes
- **Behavior gap analysis** quantifying the cost of emotional decisions
- **AI Financial Copilot** powered by Groq's LLaMA 3.3-70b model

### The Problem

Indian retail investor participation has surged, but with it comes a wave of behavioral biases:

| Bias | What Happens | Market Impact |
|------|-------------|---------------|
| **Herd Mentality** | Investors copy others instead of doing independent analysis | Speculative bubbles and crashes |
| **Panic Selling** | Emotional exits during temporary downturns | Locking in losses, missing recoveries |
| **Loss Aversion** | Pain of losses > joy of gains | Holding losers too long, selling winners too early |
| **Behavior Gap** | Buying high (FOMO) and selling low (fear) | Average investor earns 2-4% less than their investments |

SheepOrSleep provides a **data-driven "mirror"** that reflects these patterns back to the investor, guiding them toward rational, long-term wealth creation.

---

## ✨ Key Features

### 1. 🐑 Herding Detection (CCK Model)
- Analyzes **Cross-Sectional Absolute Deviation (CSAD)** across sector peers
- Uses OLS quadratic regression: `CSAD = α + γ₁|Rm| + γ₂Rm²`
- Detects statistically significant herding when **γ₂ < 0** at **p < 0.05**
- Visualizes CSAD scatter with fitted curve on interactive charts
- Reports herding intensity score (0–100)

### 2. 😰 Panic Selling Scanner
Multi-factor real-time panic detection:

| Factor | Weight | What It Measures |
|--------|--------|-----------------|
| Volume Anomaly | 30% | Z-score > 2 on down-days |
| Delivery Pressure | 20% | Low delivery % = speculative selling |
| Price-Volume Divergence | 25% | Price falling while volume surges |
| Drawdown Severity | 15% | Distance from 52-week high |
| Volatility Regime | 10% | Current vs average realized volatility |

Outputs a **Panic Score (0–100)** with severity levels: CALM → LOW → MODERATE → HIGH → EXTREME.

### 3. 💰 Behavior Gap Analysis
- Computes **Investment CAGR** (buy-and-hold returns)
- Estimates **Investor CAGR** (what average investors actually earned)
- Calculates the **Behavior Gap** — the cost of emotional trading
- Shows **10-year cost** on ₹10,00,000 of emotional decisions
- "Missing Best Days" analysis: how missing 5, 10, 15, 20, 30 best trading days destroys returns

### 4. 📊 Monte Carlo Simulation (SIP vs Panic)
- Runs **500 stochastic simulations** using historical return distributions
- Compares two investor profiles:
  - **Disciplined SIP**: Invests ₹10,000/month regardless of conditions
  - **Panic Seller**: Exits after every 10% drawdown, waits 90 days to re-enter
- Outputs wealth distribution histograms and SIP win-rate

### 5. 🤖 AI Financial Copilot
- Powered by **Groq LLaMA 3.3-70b-versatile**
- Contextual behavioral finance advisor
- Quick-action prompts for common investor questions
- Encourages SIP discipline, discourages emotional trading

### 6. 📝 Auto-Generated Conclusion
The report ends with a **clear, actionable conclusion** that summarizes all findings:
- Individual verdicts for herding, panic, behavior gap, and Monte Carlo
- Color-coded severity (green/amber/red)
- Overall assessment with specific advice

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     USER BROWSER                         │
│         Next.js 16 · React 19 · Tailwind v4             │
│         Glassmorphism UI · Recharts                      │
└─────────────────────┬────────────────────────────────────┘
                      │ HTTP / JSON
                      ▼
┌──────────────────────────────────────────────────────────┐
│                  PYTHON API SERVER                       │
│            FastAPI · Uvicorn (port 8001)                 │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  /api/analyze│  │  /api/chat   │  │  /api/stocks   │  │
│  │  One-tap     │  │  Groq LLM    │  │  Stock list    │  │
│  │  Full Report │  │  Proxy       │  │                │  │
│  └──────┬──────┘  └──────┬───────┘  └────────────────┘  │
│         │                │                               │
│  ┌──────▼──────────────────────────────────────────┐    │
│  │              ANALYTICS ENGINE                    │    │
│  │  • CCK Herding Model (OLS regression)           │    │
│  │  • Panic Detection (5-factor scoring)           │    │
│  │  • Behavior Gap (CAGR comparison)               │    │
│  │  • Missing Best Days (return decomposition)     │    │
│  │  • Monte Carlo (500 SIP vs Panic simulations)   │    │
│  └──────┬──────────────────────────────────────────┘    │
│         │                                                │
│  ┌──────▼──────────────────────────────────────────┐    │
│  │            DATA LAYER                            │    │
│  │  • yfinance (Yahoo Finance API)                 │    │
│  │  • pandas / numpy / scipy                       │    │
│  │  • 75+ NIFTY 50 & NIFTY NEXT 50 stocks         │    │
│  └─────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User** selects any Indian stock from the searchable dropdown
2. **Frontend** sends `POST /api/analyze` with stock symbol and parameters
3. **Backend** fetches live data from Yahoo Finance via `yfinance`
4. **Analytics Engine** runs all 5 analyses in sequence (~15–30 seconds)
5. **Response** returns a unified JSON blob with all metrics, chart data, and verdicts
6. **Frontend** renders the complete report with interactive Recharts visualizations
7. **Conclusion** is auto-generated on the client side from the analysis results

---

## 🛠 Technology Stack

### Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Core runtime |
| FastAPI | 0.135 | REST API framework |
| Uvicorn | 0.42 | ASGI server |
| yfinance | Latest | Yahoo Finance data (OHLCV, quotes) |
| pandas | Latest | Data manipulation |
| numpy | Latest | Numerical computation |
| scipy | Latest | Statistical testing (t-distribution) |
| Groq SDK | Latest | LLaMA 3.3-70b AI chat |
| python-dotenv | Latest | Environment config |

### Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 16.2 | React framework (App Router) |
| React | 19.0 | UI library |
| Tailwind CSS | v4 | Utility-first styling |
| Recharts | 2.15 | Interactive charts (candlestick, scatter, bar) |
| Lucide React | Latest | Icon system |
| TypeScript | 5.x | Type safety |

---

## 📂 Project Structure

```
TechKrutiVerse/
├── server.py                    # FastAPI backend — all analytics + API routes
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (GROQ_API_KEY)
├── .env.example                 # Template for .env
├── README.md                    # This documentation
│
├── binary-investor/             # Next.js 16 frontend
│   ├── app/
│   │   ├── layout.tsx           # Root layout (Inter font, metadata, SEO)
│   │   ├── globals.css          # Light glassmorphism design system
│   │   ├── page.tsx             # Main dashboard (report + conclusion)
│   │   │
│   │   ├── copilot/
│   │   │   └── page.tsx         # Dedicated AI Copilot chat page
│   │   │
│   │   ├── components/
│   │   │   ├── StockSelector.tsx # Searchable stock dropdown (sector-grouped)
│   │   │   └── Charts.tsx       # Recharts: Candlestick, CSAD, Volume, MC histogram
│   │   │
│   │   └── lib/
│   │       ├── types.ts         # TypeScript interfaces for API responses
│   │       └── stockUniverse.ts # 54 Indian stocks (NIFTY 50 + NEXT 50)
│   │
│   ├── .env.local               # Frontend env (NEXT_PUBLIC_API_URL)
│   ├── package.json
│   └── tailwind.config.ts
│
├── analytics/                   # Original Streamlit analytics modules
├── ai/                          # Original AI/LLM modules
├── config/                      # Configuration files
├── data/                        # Data utilities
├── pages/                       # Original Streamlit pages
├── ui/                          # Original Streamlit UI components
└── app.py                       # Original Streamlit entry point
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Groq API Key** (free at [console.groq.com](https://console.groq.com))

### 1. Clone the Repository

```bash
git clone https://github.com/YashHelge/TGPCET_Team_Red_Horse.git
cd TGPCET_Team_Red_Horse
```

### 2. Set Up the Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your Groq API key:
#   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxx
#   GROQ_MODEL=llama-3.3-70b-versatile

# Start the API server
uvicorn server:app --host 0.0.0.0 --port 8001
```

The API will be available at `http://localhost:8001`.

### 3. Set Up the Frontend

```bash
# Navigate to the Next.js project
cd binary-investor

# Install dependencies
npm install

# Configure API URL (already set by default)
# .env.local contains: NEXT_PUBLIC_API_URL=http://localhost:8001

# Start the dev server
npm run dev
```

The dashboard will be available at `http://localhost:3000`.

### 4. Use the Application

1. Open **http://localhost:3000** in your browser
2. Select any Indian stock from the dropdown (50+ stocks, searchable by name, symbol, or sector)
3. Click **⚡ Generate Report**
4. Wait ~15–30 seconds for all analytics to complete
5. Scroll through the full report with charts, metrics, and conclusion
6. Visit **/copilot** to chat with the AI behavioral finance advisor

---

## 📡 API Reference

### `GET /api/health`
Health check endpoint.

**Response:**
```json
{ "status": "ok", "groq": true }
```

### `GET /api/stocks`
Returns the full list of supported Indian stocks.

**Response:**
```json
{
  "stocks": [
    { "symbol": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy", "index": "NIFTY 50" },
    ...
  ]
}
```

### `GET /api/quote?symbol=RELIANCE.NS`
Real-time quote for a single stock.

**Response:**
```json
{
  "symbol": "RELIANCE.NS",
  "name": "Reliance Industries",
  "price": 2450.50,
  "changePct": 1.23,
  "volume": 12345678,
  "marketCap": 1660000000000,
  "peRatio": 28.5,
  ...
}
```

### `POST /api/analyze` ⭐ Core Endpoint
Runs **all 5 analytics** in one call and returns the complete report.

**Request Body:**
```json
{
  "symbol": "RELIANCE.NS",
  "periodDays": 365,
  "sipAmount": 10000,
  "simYears": 10,
  "nSimulations": 500
}
```

**Response Structure:**
```json
{
  "quote": { ... },              // Live stock data
  "priceChart": [ ... ],         // OHLCV time series (sampled ~120 pts)
  "herding": {                   // CCK model results
    "herdingDetected": true,
    "intensity": 72.3,
    "gamma2": -0.004521,
    "pValue": 0.0023,
    "csadData": [ ... ]          // Scatter plot data
  },
  "panic": {                     // 5-factor panic score
    "panicScore": 34.5,
    "level": "MODERATE",
    "factors": { ... },
    "volumeData": [ ... ]        // Volume chart data
  },
  "behaviorGap": {               // CAGR comparison
    "investmentCagr": 18.45,
    "investorCagr": 14.23,
    "behaviorGap": 4.22
  },
  "missingDays": [ ... ],        // Missing best days scenarios
  "monteCarlo": {                // SIP vs Panic simulation
    "costOfPanic": {
      "meanLoss": 423000,
      "winRate": 87.2
    },
    "histogram": [ ... ]
  }
}
```

### `POST /api/chat`
Groq LLM proxy for the AI copilot.

**Request Body:**
```json
{
  "messages": [
    { "role": "user", "content": "Should I sell during a market crash?" }
  ],
  "context": "Stock: Reliance Industries\nPrice: ₹2450"
}
```

---

## 📈 Analytics Deep Dive

### CCK Herding Model

The **Chang, Cheng & Khorana (2000)** model detects herding by analyzing return dispersion:

```
CSAD_t = α + γ₁|R_m,t| + γ₂R²_m,t + ε_t
```

Where:
- **CSAD** = Cross-Sectional Absolute Deviation (how much stocks deviate from sector average)
- **R_m** = Sector market return (cross-sectional average)
- **γ₂ < 0 and significant** → Herding detected (returns cluster during extreme moves)

The system fetches all stocks in the same sector, computes daily CSAD, runs OLS regression, and tests γ₂ significance using the t-distribution.

### Monte Carlo Simulation

The system runs 500 parallel simulations using:
- **Return distribution**: Estimated from historical daily returns (`μ`, `σ`)
- **SIP profile**: Invests ₹10,000 on every 21st trading day
- **Panic profile**: Same SIP + exits all positions when drawdown hits 10%, waits 90 trading days in cash

This produces wealth distribution histograms comparing outcomes — typically showing SIP wins 70–90% of the time.

---

## 🎨 Frontend Components

| Component | File | Description |
|-----------|------|-------------|
| **StockSelector** | `components/StockSelector.tsx` | Searchable dropdown with sector grouping, index badges, 54 stocks |
| **CandlestickChart** | `components/Charts.tsx` | OHLC candlestick bars with close-price line overlay |
| **CSADScatter** | `components/Charts.tsx` | Scatter plot with CCK fitted curve (dashed regression line) |
| **VolumeChart** | `components/Charts.tsx` | Volume bars color-coded: purple = normal, red = panic day |
| **MCHistogram** | `components/Charts.tsx` | Side-by-side histogram: SIP (green) vs Panic (red) |
| **MissingDaysChart** | `components/Charts.tsx` | Horizontal bar chart showing return erosion |
| **ScoreRing** | `page.tsx` (inline) | Circular conic-gradient ring for panic score visualization |
| **AI Copilot** | `copilot/page.tsx` | Full-page chat with conversation starters |

### Design System

- **Theme**: Light glassmorphism with warm cream background (`#F4F2EE`)
- **Glass cards**: `rgba(255, 255, 255, 0.55)` + `backdrop-filter: blur(20px)`
- **Color palette**: Indigo accent (`#4F46E5`), Emerald up (`#059669`), Red down (`#DC2626`)
- **Typography**: Inter (sans-serif) via Google Fonts
- **Animations**: Fade-up on scroll, shimmer loading placeholders

---

## 🔐 Environment Variables

### Backend (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes* | — | Groq API key for AI Copilot (*optional if not using chat) |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | Groq model identifier |

### Frontend (`.env.local`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8001` | Python API server URL |

---

## 📸 Screenshots

The dashboard features a light glassmorphism design with:

- **Navbar** with SheepOrSleep brand and AI Copilot link
- **Hero** with searchable stock selector and "Generate Report" button
- **Section 01**: Stock overview with candlestick chart and key metrics
- **Section 02**: CCK herding detection with CSAD scatter plot
- **Section 03**: Panic score ring with 5-factor breakdown and volume chart
- **Section 04**: Behavior gap, missing best days, and Monte Carlo histogram
- **Section 05**: Auto-generated conclusion with color-coded verdicts
- **Footer** with attribution and navigation

---

## 📚 Research Background

This project implements peer-reviewed behavioral finance research:

1. **Chang, Cheng & Khorana (2000)** — "An examination of herd behavior in equity markets" — Econometric framework for detecting herding via CSAD non-linearity.

2. **Indian Market Herding** — Evidence of pronounced herding in Indian capital goods and IT sectors during down-markets, with banking showing more independent behavior. *(Traces of Herd Behaviour in Indian Stock Markets, ResearchGate)*

3. **Panic Selling Prediction** — ML models incorporating volume anomalies, delivery percentages, and drawdown patterns to predict "freak-out" events. *(DSpace@MIT, 2022)*

4. **Behavior Gap** — The difference between investment returns and investor returns, typically 2–4% CAGR for Indian retail investors due to poor timing. *(Morningstar India; AssetPlus)*

5. **Hyperbolic Discounting** — Investors prioritize immediate emotional relief over long-term gains, driving panic selling during temporary corrections. *(PMC, 2024)*

6. **Missing Best Days** — Sitting out during volatility and missing just 10 best days in a 20-year cycle can reduce returns by over 50%. *(310 Wealth Planning; BillCut)*

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Tips

- Run the backend in dev mode: `uvicorn server:app --reload --port 8001`
- Run the frontend: `cd binary-investor && npm run dev`
- API docs are auto-generated at `http://localhost:8001/docs` (Swagger UI)

---

## 📄 License

This project is for **educational purposes only**. It is not financial advice. Always consult a certified financial advisor before making investment decisions.

---

<p align="center">
  <strong>Built with ❤️ by Team Red Horse (TGPCET)</strong>
  <br />
  <em>Making Indian retail investors smarter, one bias at a time.</em>
</p>