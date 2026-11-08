# SheepOrSleep (binary-investor): Engineering Teardown and Production Blueprint

*Prepared for Kritish Bokde. Repo `KritishBokde91/binary-investor`, commit `feb37ef` (single commit, 24 Mar 2026). Review date: 8 Nov 2026.*

## 0. Method, evidence labels, and what to settle first

I cloned the repo and read every source file (about 40 Python and TypeScript files). Wherever a claim could be tested, I executed your own functions: I imported `server.py` unmodified, stubbed the network and framework imports, fed it controlled synthetic data, and recorded the output. Every finding carries one label:

- **\[RAN\]** I executed the repo's code and measured the result.
- **\[READ\]** Established by reading the code at the cited line; not executed.
- **\[EST\]** Arithmetic estimate from stated assumptions.
- **\[WEB\]** Checked against external sources.

Limits of this review: Yahoo Finance is not reachable from my sandbox, so nothing here depends on live market data. I did not run `npm install`, the Next.js build, or lint, so frontend findings are \[READ\]. Nothing here is legal advice. Library recommendations name tools, not versions; pin the latest stable release when you adopt them.

Two things to settle before this becomes your flagship project:

1. **Attribution.** The README credits "Team Red Horse (TGPCET)", its clone command points to `YashHelge/TGPCET_Team_Red_Horse`, and its tree diagram says `TechKrutiVerse/`. The repository has one commit. That is normal for a hackathon origin, but interviewers read READMEs. Your resume should claim what you personally build in this upgrade, and the README should state plainly what is hackathon origin and what is new.
2. **README claims the code does not support** (listed in section 1.5). In fintech, an overstated README costs more credibility than a modest one.

## Executive summary: the ten findings that matter most

1. **The system can tell users everything is fine when it has no data. \[RAN\]** I simulated Yahoo returning HTTP 429 and called your real `analyze()`. Result: HTTP 200, price 0, panic "NO DATA", behavior gap 0, empty missing-days list. But `simulate_sip_vs_panic` still returns a full Monte Carlo built from hard-coded fallback parameters (`server.py:394-395`). The frontend's `getConclusion()` (`page.tsx:285-305`) sees zero flags and renders "Healthy Market Conditions... rational investor behavior." For a risk product this is the worst bug in the repo.
2. **"Behavior Gap" is not measured; it is a formula that cannot detect behavior. \[RAN\]** `gap = max(0, corr(volume, price) * buy-and-hold CAGR * 0.4)` (`server.py:344-348`, `behavior_gap.py:147-154`). On four synthetic stocks: a rising stock with volume at highs gets a 10.5-point "gap"; a falling stock with the same volume pattern gets 0; a falling stock with contrarian volume gets a positive gap that lowers "investor CAGR" further. The README says it estimates "what average investors actually earned." No investor data enters the calculation.
3. **CAGR is overstated by about 48% in Missing-Best-Days. \[RAN\]** `** (365 / len(daily_returns))` (`server.py:379`, `behavior_gap.py:57-59`) divides calendar days by a trading-day count. On a synthetic 10-year series with a true 10.24% CAGR it reports 15.16%.
4. **The Monte Carlo headline is a function of one noisy assumption. \[RAN\]** "SIP beats panic selling X% of the time" ranges from 41% (0% drift) to 93% (20% drift) at the same volatility. Drift estimated from the at-most-5 years of data the code uses (`server.py:393`) has a standard error near 10 percentage points annualised \[EST\]. The UI shows one number and no uncertainty.
5. **20% of the panic score is effectively a constant zero. \[RAN\]** "Delivery Pressure" is not delivery data. It is a high-low range ratio that only fires when today's range exceeds 3.5x its 20-day average. On 1,000 synthetic calm markets it fired in 0.4%.
6. **One request fans out to about 15 sequential Yahoo calls with no cache. \[READ/EST\]** Details in section 2.1.
7. **Open, unbounded endpoints. \[READ/RAN\]** No auth, no rate limit, unbounded `simYears` and `nSimulations`, and `/api/chat` forwards client-controlled roles and context into your Groq prompt.
8. **CORS reflects any origin with credentials enabled. \[RAN\]** Latent today (no cookies), a hole the day you add sessions.
9. **Two diverging implementations and three stock universes. \[READ/RAN\]** `server.py` imports nothing from `analytics/`, `data/`, `ai/` or `config/`; it re-implements them.
10. **No tests, CI, containers, database, auth, or observability; Python dependencies unpinned. \[READ\]** And the static universe is already stale: NSE renamed `ZOMATO` to `ETERNAL` on 9 Apr 2025 and `TATAMOTORS` to `TMPV` on 24 Oct 2025, with the commercial-vehicle arm listed separately on 12 Nov 2025 \[WEB\]. All before your first commit.

### What is genuinely good (keep it)

- The CCK herding regression is mathematically correct OLS with proper standard errors, and it behaves conservatively rather than crying wolf \[RAN, section 2.2\].
- The panic score did not false-alarm on 1,000 calm synthetic markets (max 30.8/100, 0.2% reached "MODERATE") \[RAN\].
- Secret hygiene is clean: `.env` is ignored, `.env.example` is a placeholder, and a scan of the full history found only the README's `gsk_xxx` placeholder \[RAN\].
- The system prompt forbids buy/sell recommendations (`server.py:545-548`). Right instinct; it needs enforcement beyond a prompt.
- Frontend `types.ts` matches the server's response keys; I found no contract drift \[RAN script\].
- Behavioral finance grounded in real literature (Chang, Cheng and Khorana, 2000) is a strong portfolio narrative. The upgrade path below keeps that narrative and makes it defensible.

## 1. Pillar 1: Codebase and architecture audit

### 1.1 Architecture as built

The repo contains **two parallel applications**:

- **Legacy:** a Streamlit multi-page app (`app.py`, `pages/1-5`, `ui/`, `analytics/`, `ai/`, `data/`, `config/`). Class-based, uses `st.cache_data`.
- **Current:** a FastAPI monolith `server.py` (571 lines, 5 routes) plus a Next.js 16 frontend in the nested folder `binary-investor/binary-investor/`.

**Data pipeline (current):** browser `POST /api/analyze {symbol}` -> one synchronous handler -> seven compute functions run sequentially -> each calls `yfinance` directly -> pandas/numpy -> one JSON blob -> React `useState` -> a client-side `getConclusion()` produces the verdict text.

**State management:** the server is stateless: no database, no cache, no sessions. The client holds everything in component state; chat history lives in `useState` and is lost on navigation.

**API design:** `GET /api/stocks`, `GET /api/quote`, `POST /api/analyze`, `POST /api/chat`, `GET /api/health`. No versioning, no auth, no pagination, no `response_model` (handlers return raw dicts, so OpenAPI documents nothing about responses and `types.ts` is hand-maintained). Errors return HTTP 200 with an error string or zero-filled payload.

**Port inconsistency \[READ\]:** `server.py:571` serves on 8000; the README says 8001; `page.tsx:20` and `AICopilot.tsx:14` default to 8000; `copilot/page.tsx:12` defaults to 8001; and the frontend's `.gitignore` excludes `.env*`, so the README's "`.env.local` already set" is not true of a fresh clone. On default settings one of the two chat surfaces is always broken.

### 1.2 File-by-file audit

| File | Role | Main problems |
| --- | --- | --- |
| `server.py` (571) | God-module: config, universe, data access, 5 analytics, 5 routes | Imports nothing from the rest of the repo (full re-implementation). Universe hard-coded at `:39-117`. Exception swallowing at `:139`, `:166`, `:217`, `:248`. Unbounded request model `:503-508`. Per-request Groq client `:544`. Error text leaked at `:561`. Unseeded RNG `:405`. |
| `analytics/herd_detector.py` | CCK/CSAD herding, class-based | `@st.cache_data` on methods with `_self` (`:166-167`, `:205-206`) ignores instance state, so changing the lookback returns stale results \[RAN\]. Rolling window of 30 observations for a 3-parameter regression (`:156-164`). Invented intensity `:117-120`. Domain code imports Streamlit. |
| `analytics/panic_detector.py` | 5-factor panic score | Delivery factor is a range ratio, not delivery (`:56-83`). Denominators differ from `server.py` (`:134` vs `server.py:267`), so the two apps score the same stock differently. |
| `analytics/behavior_gap.py` | Behavior gap + best-days | Invented gap formula `:147-154`. CAGR exponent bug `:57-59`. `compute_worst_timing_analysis` computes only the DCA curve despite its docstring promising worst/best timers (`:77-123`). |
| `analytics/portfolio_simulator.py` | Monte Carlo | Entire simulation duplicated for the fallback path (`:160-254`). Pure-Python day loop. iid Normal returns. |
| `data/stock_data.py` | yfinance access + indicators | `st.warning` inside the data layer (`:47`). RSI uses a simple rolling mean instead of Wilder smoothing (`:148-149`), so it will not match any charting platform. |
| `data/market_indicators.py` | Breadth, sector performance, vol regime | Sequential per-symbol fetches in loops. "Market breadth" is a sample of about 24 stocks (`:28-31`). "VIX proxy" instead of the real India VIX. |
| `data/news_sentiment.py` | Google News RSS + sentiment | XML parsed with regex (`:31-39`). Greedy `\{.*\}` JSON extraction (`:90`). Bare `except: pass` (`:110`). Keyword fallback uses substring matching (`:131-132`), so "up" matches "group" and "low" matches "follow". Headlines go to the LLM unsanitised. |
| `ai/groq_client.py` | LLM wrapper | `temperature or self.temperature` (`:63`, `:105`) can never pass 0.0. Retry detection by string-matching error text (`:70`). Returns error strings as if they were model output, which callers then parse as data. Calls `st.error` from a client class. |
| `ai/nudge_engine.py` | Prompted nudges | Prompts ask the model for "historical examples" (`:63`) and "real SIP success stories in Indian mutual funds" (`:97`): an invitation to hallucinate facts to retail users. |
| `config/stock_universe.py` | Universe (83) | Includes three index tickers in a "stock" list (`^NSEI`, `^BSESN`, `^NSEBANK`). Static; already stale. |
| `config/settings.py` | Settings | Evaluated at import, no validation. `MONTE_CARLO_SIMULATIONS=1000` vs 500 in `server.py`. |
| `binary-investor/app/page.tsx` (889) | Entire dashboard | One client component. Stale-response race at `:261-280`. Business logic (`getConclusion`) in the view. |
| `app/components/AICopilot.tsx`, `app/copilot/page.tsx` | Two chat UIs | Duplicated chat logic; the panel sends context, the page sends `context: ""` (`copilot/page.tsx:49`). Full history resent every turn, no truncation. |
| `app/components/Charts.tsx` (455) | Recharts | Several `any` props (`:23`, `:30`, `:55`). |
| `requirements.txt` | Deps | 13 unpinned lines; `scikit-learn` and `beautifulsoup4` unused; Streamlit and Plotly shipped with an API. |
| `package.json` | Deps | `yahoo-finance2` is declared but never imported. |

### 1.3 Anti-patterns, races, edge cases (with locations)

1. **Silent failure by design \[RAN\].** Every data function returns an empty frame or zeros on any exception. Combined with HTTP 200 and the client-side verdict logic, outage and "calm market" are indistinguishable (finding 1).
2. **Stale-response race \[READ\].** `analyze()` (`page.tsx:261-280`) has no `AbortController` or request id, and the selector calls it directly on selection (`:377`). Select stock B while A is in flight and A's slower response overwrites B's result; A's `setLoading(false)` also clears B's spinner. The page can display one company's analysis under another's name.
3. **Cache keyed on the wrong thing \[RAN\].** With the repo's own pattern (`@st.cache_data` on a method with `_self`), `HerdDetector(90)` and `HerdDetector(730)` both returned "period\_days=90". The Streamlit herding page lets the user choose the lookback (`pages/2_Herd_Detector.py:37-48`), so users see stale numbers after changing it.
4. **Same ticker downloaded six times per request \[READ\].** Windows of 365 (chart), 365 (herding), 180 (panic), 730 (gap), 1,095 (best-days) and 1,825 days (Monte Carlo). One 5-year fetch sliced six ways would do.
5. **Blocking, CPU-bound work in the request path \[RAN\].** The Monte Carlo (500 paths x 2,520 days x 2 profiles) takes 0.89 s of pure-Python loop on my machine. Python threads do not parallelise it (GIL).
6. **Time handling \[READ\].** `end=datetime.now()` (`server.py:127`) uses the server's local clock; yfinance's end bound is exclusive, so today's bar is missing; there is no IST/UTC handling.
7. **`df.dropna(inplace=True)` (`server.py:135`)** discards any row with a NaN in any column, including legitimate zero-volume days.
8. **Panic seller buys on its exit day \[READ\].** After `in_mkt = False` (`server.py:420`), the SIP purchase on the next line still executes in the same branch (`:421`). Small effect, but it means the "out of market" profile is occasionally in.
9. **Unbounded growth, not classic leaks.** I found no true memory leak in the stateless FastAPI path. The realistic memory risks are the Streamlit `st.cache_data` caches (no `max_entries`) and array sizes driven by the unbounded `simYears`.
10. **Unbounded chat context.** The server concatenates whatever history the client sends (`server.py:552`); the client resends all of it every turn.

### 1.4 Database: there isn't one

You asked for a schema, indexing and concurrency review. The honest answer: **there is no database, no persistence, no user model and no transaction anywhere in the repo.** Consequences: no history of what the product told a user (no audit trail for generated "advice"), no caching tier, nothing to scale horizontally, and no way to compute anything ahead of time. The target schema (instruments with symbol history, TimescaleDB bar hypertable, versioned analysis results) is in section 3.4.

### 1.5 README versus reality

| README says | Code says |
| --- | --- |
| "production-ready" | No tests, CI, containers, auth, persistence |
| "Estimates Investor CAGR (what average investors actually earned)" | Volume-price correlation times CAGR times 0.4 |
| Drawdown "Distance from 52-week high" | Drawdown from the high of the *analysis window* (90-180 days), `server.py:284` |
| "Delivery Pressure: Low delivery % = speculative selling" | A high-low range ratio; no delivery data |
| "75+ NIFTY 50 & NEXT 50 stocks" | 77 in `server.py`, 83 in `config/`, 54 in the frontend |
| "Recharts 2.15" | `package.json` pins `^3.8.0` |
| "`tailwind.config.ts`" in the tree | File does not exist (Tailwind v4 is CSS-first) |
| "Monte Carlo: SIP wins 70-90% of the time" | True only if you assume 10-15% drift (section 2.2) |
| Port 8001 | `server.py` serves 8000 |

## 2. Pillar 2: Real-world failure modes and limitations

### 2.1 System bottlenecks

**Per-request cost model \[READ\].** For a Banking stock (9 symbols in `server.py`'s universe): 1 quote via `Ticker.info`, 1 chart, 9 peer histories for herding, then panic, gap, best-days and Monte Carlo = **15 outbound Yahoo calls**, one after another, inside a single threadpool slot. For a stock in a sector with fewer than 3 peers (15 of 77 symbols) herding exits early and it is 6 calls. There is no cache anywhere in `server.py`: the Streamlit app's `st.cache_data` was lost in the port.

**Throughput ceiling \[EST\].** FastAPI runs sync `def` handlers in AnyIO's threadpool (default limit 40 threads), and `uvicorn.run(app, ...)` (`server.py:571`) starts one process, so one GIL. Your README quotes 15-30 s per analysis. By Little's law, 40 slots / 15 s is about 2.7 requests/s at best (1.3/s at 30 s). Ten thousand simultaneous users would need at least an hour to drain even if Yahoo never failed, and clients would time out long before that.

**Third-party failure matrix.**

| Dependency | Failure | What happens today | Required behavior |
| --- | --- | --- | --- |
| Yahoo 429 / timeout | `except Exception` returns empty frame | HTTP 200, zeros, "Healthy" verdict (finding 1) | Explicit `degraded` status; serve last-good with `as_of`; never render a verdict |
| Yahoo partial history | `dropna`, shorter sample | Herding silently uses the *shortest* peer history after the inner join (`server.py:196`) | Data-quality gate with minimum observations; report n |
| Groq 429 / 5xx / timeout | `except` returns 200 with "Error: {e}" text | Error shown as an assistant message; internals leaked | Typed error, jittered retry, circuit breaker, fallback model, clear UI state |
| Google News (Streamlit only) | `st.warning`, empty list | Sentiment section silently blank | Cached last-good; source-health metric |
| Corporate action (rename, demerger) | Symbol now means a different entity or series breaks | CAGR, drawdown, panic wrong, no warning | Security master with symbol history and adjustment factors |

**Volatility spikes.** The product is used most when markets are stressed, which is exactly when Yahoo throttles and when everyone opens the same crashing stock. With no cache and no single-flight, N concurrent users on one symbol cost 15N upstream calls. And the panic score's volume z-score is mathematically capped (section 2.2), so it is least able to register the biggest spikes.

**LLM path.** A new `Groq` client per request (`server.py:544`), no timeout (a hung upstream pins a thread), no streaming, unbounded history, and Groq's limits are per key, so every user shares one quota.

### 2.2 Algorithmic and model flaws

**A. Behavior Gap (finding 2).** Besides using no investor data, the normalisation `(close - min) / (max - min)` (`server.py:345`) uses full-sample extremes, a look-ahead construction. And the correlation of *volume* with *price level* mostly reflects trend and liquidity growth, not mistimed trades. Four synthetic stocks through the repo's `compute_behavior_gap` \[RAN\]:

| Scenario | Buy-and-hold CAGR | "Investor CAGR" | Gap |
| --- | --- | --- | --- |
| Rising, volume at highs | 29.70% | 19.21% | 10.49 |
| Rising, volume at lows (contrarian) | 29.70% | 29.70% | 0.00 |
| Falling, volume at highs | -8.57% | -8.57% | 0.00 |
| Falling, volume at lows | -8.57% | -11.15% | 2.58 |

Sign and size are driven by whether the stock rose, which is the opposite of what a behavior gap should isolate.

**B. Missing Best Days.** Beyond the exponent bug (finding 3): the analysis removes best days but not worst days. Best and worst days cluster in the same high-volatility regimes, so removing only the best overstates the cost of being out; the honest version also shows "missed best and worst". It is hindsight by construction (acceptable as an illustration if labelled), and cash earns 0% (`server.py:374`) instead of a liquid-fund or T-bill rate.

**C. Monte Carlo.**

- Returns are iid Normal at the sample mean and standard deviation (`server.py:405`). Real returns have fat tails, volatility clustering and crash regimes, and the panic rule being modelled is triggered by exactly those drawdowns. iid Normal understates their frequency and depth.
- **The headline is mostly a drift assumption \[RAN\].** Your own `simulate_sip_vs_panic`, 500 paths, 10 years, with (mu, sigma) set exactly. Cells are "SIP beats panic" win rate in %:

| Annual drift | Vol 18% | Vol 23.8% | Vol 32% |
| --- | --- | --- | --- |
| 0% | 44.4 | 41.4 | 39.0 |
| 5% | 65.0 | 60.2 | 52.0 |
| 10% | 77.4 | 74.6 | 66.0 |
| 12.6% | 83.4 | 81.8 | 71.2 |
| 15% | 88.0 | 87.6 | 77.0 |
| 20% | 94.4 | 92.8 | 85.2 |

- The sampling standard error of a drift estimated from 5 years of daily data at 1.5% daily volatility is 0.015 / sqrt(1260), about 0.042% per day, or roughly **10.6% annualised** \[EST\]. That is the size of the drift itself, so an honest 95% interval on "SIP wins X%" spans roughly 40% to 90%. The UI shows one number.
- Unseeded: five identical calls returned 23.2% to 27.6% \[RAN\]. Monte Carlo error at 500 paths is about plus or minus 2 points \[EST\]; show it or use more paths.
- The behavior model is arbitrary (exit at -10% from peak, wait 90 days, cash earns 0, no brokerage, STT, tax, exit load or slippage) and calibrated to no observed investor behavior.
- Survivorship bias: the universe is today's index members, so every historical statistic is conditioned on having made it into the index.

**D. Herding (CCK).** I tested `compute_herding` \[RAN\] under a null with no herding by construction (factor model, fat tails, volatility clustering, 245 days), then with a planted concave CSAD relationship. I expected inflated false positives from the missing HAC correction. **That hypothesis was wrong.** The detector flagged herding in only 0.8% to 1.8% of null trials, because it applies a two-sided p-value (`2 * (1 - cdf)`, `server.py:220`) to a one-sided hypothesis. It is conservative, so the cost is lost power:

| Cross-section | Planted curvature | Repo detects | Newey-West, one-sided |
| --- | --- | --- | --- |
| 3 stocks | weak | 10.7% | 21.3% |
| 3 stocks | strong | 47.3% | 70.3% |
| 5 stocks | strong | 64.0% | 77.0% |
| 9 stocks | strong | 75.0% | 83.3% |

Caveat: Newey-West is itself over-sized at N=3 (11.3% false positives under the null), so at small N a bootstrap is the right tool and a larger cross-section is the real fix. Other issues:

- **Cross-section too small.** 15 of 77 stocks sit in sectors with fewer than 3 peers, where the endpoint returns an error object inside an HTTP 200. Sectors with exactly 3 stocks (Capital Goods, Consumer Durables, Cement, Power) are statistically meaningless.
- **Wrong unit of inference.** The result is about a sector, but the UI presents it as a verdict on the selected stock.
- **Invented intensity.** For detected herding it is `|gamma2 / gamma1| * 100` capped at 100; for non-herding it is `min(20, |gamma2| * 1000)` (`server.py:222`), so strong **anti-herding** (gamma2 > 0, dispersion rising in extreme markets) is reported as 20/100 \[RAN\].
- The rolling version regresses 3 parameters on 30 observations (`herd_detector.py:156-164`) and rescales gamma2 by 10,000 (`:160`) with no justification.
- "Market" is the sector mean, and sector peers share common factors, so CSAD dynamics are partly mechanical.

**E. Panic score \[RAN\].**

- **Delivery proxy.** `est_del < 30` is equivalent to `range / avg_range > 3.5`. It fired in 0.4% of calm markets, so 20% of the weight is dead. NSE publishes real delivery quantity and percentage in its daily security-wise files, so the proxy is unnecessary and the factor name misleads.
- **Z-score contamination.** The 20-day window includes today (`server.py:262`, `panic_detector.py:38-40`). A spike of k prior-sigmas reads: 2 sigma gives 1.77, 3 gives 2.41, 5 gives 3.20, 10 gives 3.90. The hard ceiling is (n-1)/sqrt(n) = 4.25 for n=20, so the largest panic days saturate. Fix: lagged window, plus a robust median/MAD z-score on log volume.
- **Drawdown factor** measures from the analysis window's high, not the 52-week high the README claims, and averaged 42/100 on driftless calm markets, so the least behavioral factor dominates calm-market scores.
- **Window counting.** A panic day five months ago counts as much as yesterday's, yet the score is presented as current.
- **Uncalibrated.** Weights (30/20/25/15/10), scalers (x500, x200) and thresholds (10/30/50/70) connect to no outcome. In fairness, it did not false-alarm (section 0), so the problem is that it is unvalidated, not that it is noisy.

**F. Look-ahead bias and leakage.** In the forecasting sense there is none, because nothing is predicted, which is also why the score cannot be validated. The look-aheads that do exist are the full-sample normalisation (A) and the hindsight best-day removal (B). The moment you add any predictive model (Pillar 4), leakage becomes the main risk and requires purged cross-validation.

**G. LLM content risk.** Prompts ask for "historical examples of herding in Indian markets" and "real SIP success stories" (`nudge_engine.py:63`, `:97`) with no retrieval or citation. The model will produce plausible, unverifiable specifics, shown to retail users in a product whose value is credibility.

**H. Static universe \[WEB\].** NSE changed `ZOMATO` to `ETERNAL` (9 Apr 2025) and `TATAMOTORS` to `TMPV` (24 Oct 2025); the commercial-vehicle arm was listed separately on 12 Nov 2025 (NSE circulars as reported by Upstox, HDFC Sky, Business Standard). I did not test how Yahoo handles either, and vendors treat demergers inconsistently. Whatever it does, the repo has no mechanism to notice a discontinuity.

### 2.3 Security and compliance

| Area | Finding |
| --- | --- |
| AuthN / AuthZ | None on any route \[READ\] |
| Rate limiting | None \[READ\] |
| CORS | `allow_origins=["*"]` with `allow_credentials=True` (`server.py:27-33`). Starlette reflects the caller's Origin: a preflight from `https://evil.example` received `Access-Control-Allow-Origin: https://evil.example` and `Allow-Credentials: true` \[RAN\]. Harmless today; a credentialed cross-origin hole once cookies exist. |
| Input validation | `symbol` unvalidated on `/api/analyze` and `/api/quote`. `periodDays`, `simYears`, `nSimulations` unbounded (`:503-508`). 500 paths x 10 years costs 0.89 s \[RAN\]; cost is linear, so 1,000,000 paths is about 30 minutes of one worker \[EST\]. |
| LLM abuse and injection | `messages: list[dict]` accepts any role including `system` (`:534`); `context` is appended to the system prompt (`:549-550`). It is an unauthenticated proxy to your Groq key with an attacker-editable system prompt. |
| Error handling | Exceptions return `str(e)` with HTTP 200 (`:561`): leaks internals, defeats monitoring, hides failure from clients. |
| Secrets | History is clean \[RAN\]. But: one shared key read at import, no rotation or scoping, no secret scanning in CI. |
| Supply chain | `requirements.txt` has no versions; unused packages widen the attack surface; no `pip-audit`, `npm audit`, Dependabot or SBOM. |
| Injection (Streamlit) | Raw LLM output interpolated into HTML with `unsafe_allow_html=True` (`pages/2:195`, `3:232`, `4:194`, `4:349`, `5:203`); news headlines interpolated into Markdown (`pages/3:223`). The Next.js path uses `react-markdown`, safe by default unless `rehype-raw` is added \[READ, not built\]. |
| Data integrity and provenance | Nothing persisted; no `as_of` on quotes; no version on data or models. Users cannot tell stale, fallback or degraded results from real ones. With no transactions in the system, this is the integrity problem. |
| Transport and headers | No TLS, HSTS or CSP story; `NEXT_PUBLIC_API_URL` exposes the backend URL. |

**Compliance (India). Confirm with a qualified lawyer; I am not one.**

- **SEBI.** The UI emits directive language: "Set a clear stop-loss and target before entering any position", "Consider a systematic SIP strategy", and color-coded verdicts (`page.tsx:297-335`). Regulators look at substance, not disclaimers. Choose deliberately between (a) educational positioning with strict content controls and no individualized guidance, or (b) the registration path under the Investment Advisers or Research Analysts regulations. Do not drift into (b) by accident.
- **Data licensing.** yfinance's documentation says it is intended for research and educational use and defers to Yahoo's terms for data rights. Commercial redistribution of exchange data generally needs licences; plan a licensed or broker-API source before any paid tier.
- **DPDP Act 2023.** Once you store accounts, consent, purpose limitation, retention and deletion apply. Check the current status of the implementing rules.
- **Audit trail.** Persist every generated "nudge" with its inputs, model version and prompt version.

## 3. Pillar 3: Enterprise-grade architecture and stack upgrades

### 3.0 The principle that fixes most of Pillar 2

Everything this product computes is a function of daily bars. Compute it once per symbol per day, store it versioned, and serve it from cache. Then 10,000 concurrent users is a read-scaling problem (CDN, Redis, a read replica), and the expensive compute scales with the number of symbols (hundreds), not users. Streaming infrastructure is only justified once you ingest intraday ticks. Build the batch path first, and be ready to say why in an interview: knowing what not to build is a senior signal.

### 3.1 Target architecture

&#91;embedded content: target architecture · read path, write path, 9 components\]

The read path never touches an upstream provider. The write path is scheduled and event-driven, and it is the only place provider outages are handled. Each Pillar 2 failure maps to a specific fix:

| Problem | Fix |
| --- | --- |
| 15 sequential Yahoo calls per request | Ingest once per day per symbol; the request path touches only Redis and Postgres |
| Silent zeros leading to a "Healthy" verdict | Result envelope with `status`, `as_of`, `data_version`; the UI renders degraded states and suppresses the verdict |
| Open, unbounded endpoints | Gateway auth and per-key rate limits; Pydantic bounds; role allowlist on chat |
| Two diverging codebases | One `analytics` package imported by workers and API; retire the Streamlit app or make it a thin API client |
| Stale universe, broken series | Security master with symbol history, corporate-action table, nightly constituent sync |
| Verdict logic in the browser (`page.tsx:285`) | Compute the verdict server-side with provenance; the client only renders it |

### 3.2 Event-driven pipeline, sized to the load

- **Start with Redis Streams** (or ARQ, Taskiq or Celery on Redis). Use consumer groups, acknowledgements, a dead-letter stream, and idempotent handlers keyed by `(instrument_id, trading_date, kind, data_version)`.
- **RabbitMQ** if you need routing topologies and per-message TTL and retry semantics. **Kafka or Redpanda** only when you ingest intraday ticks, need multi-consumer replay, or outgrow one broker. At end-of-day scale (hundreds of symbols) Kafka is operational cost with no benefit.
- **On-demand analysis** (custom parameters): `POST /v1/analyses` returns `202` with a job id; `GET /v1/analyses/{id}` or SSE streams status. Deduplicate by `(symbol, params_hash, data_version)` so repeats are cache hits.
- **Stampede control:** single-flight lock (`SET key NX PX`), stale-while-revalidate, jittered TTLs.
- **Outbox pattern** when a worker must write a result row and publish an event atomically.

### 3.3 Data layer and resilience

- A `MarketDataProvider` protocol with adapters: a licensed or broker source as primary (for example a broker API such as Kite Connect, Upstox or Angel One SmartAPI, or a data vendor), NSE's daily archives for end-of-day bars and delivery data, and yfinance for development only. Check each provider's terms for your intended use.
- Per-provider bulkhead and circuit breaker (`purgatory` or `pybreaker`), `tenacity` retries with exponential backoff and jitter, `aiolimiter` for client-side limits, and one shared `httpx.AsyncClient` with explicit timeouts.
- Replace silent zeros with a typed envelope:

```python
class Result(BaseModel, Generic[T]):
    status: Literal["ok", "stale", "degraded", "unavailable"]
    as_of: datetime | None
    data_version: str
    value: T | None
    reason: str | None = None
```

The frontend renders `degraded` and `unavailable` explicitly and **suppresses the verdict** unless every input is `ok`. This removes finding 1 by construction.

- **Security master:** an `instrument_id` independent of ticker, symbol history with validity dates, ISIN, a corporate-action table with adjustment factors, and a nightly constituent sync. A NIFTY 500 universe gives 20+ names per sector, which also fixes herding. ZOMATO to ETERNAL and TATAMOTORS to TMPV/TMCV become data changes, not code changes.

### 3.4 Database and storage

Postgres with TimescaleDB over InfluxDB: you need relational joins (instruments, users, results) and SQL. InfluxDB earns a place only for tick-scale metrics.

```sql
CREATE TABLE instruments (
  instrument_id bigserial PRIMARY KEY, isin text UNIQUE NOT NULL,
  name text NOT NULL, sector text NOT NULL, listed_on date, delisted_on date);
CREATE TABLE instrument_symbols (
  instrument_id bigint NOT NULL REFERENCES instruments, symbol text NOT NULL,
  valid_from date NOT NULL, valid_to date,
  PRIMARY KEY (symbol, valid_from));
CREATE TABLE bars_1d (
  instrument_id bigint NOT NULL, ts date NOT NULL,
  open numeric(14,4), high numeric(14,4), low numeric(14,4), close numeric(14,4),
  volume bigint, deliv_qty bigint, adj_factor numeric(18,10) NOT NULL DEFAULT 1,
  source text NOT NULL, ingested_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (instrument_id, ts));
SELECT create_hypertable('bars_1d', 'ts', chunk_time_interval => INTERVAL '1 year');
CREATE TABLE analysis_results (
  instrument_id bigint NOT NULL, kind text NOT NULL, params_hash text NOT NULL,
  data_version text NOT NULL, model_version text NOT NULL,
  computed_at timestamptz NOT NULL DEFAULT now(), payload jsonb NOT NULL,
  PRIMARY KEY (instrument_id, kind, params_hash, data_version));
CREATE INDEX ON analysis_results (instrument_id, kind, computed_at DESC);
```

- The `bars_1d` primary key already serves per-instrument range scans, so no extra index is needed. Compress chunks older than a year; use continuous aggregates for weekly and monthly bars. Store raw bars and adjustment factors separately from adjusted series so corporate actions can be corrected retroactively.
- `analysis_results` is append-only and versioned: reproducibility and an audit trail for free.
- **Concurrency:** PgBouncer in transaction mode, `asyncpg` or SQLAlchemy 2.0 async, the API on a read replica and workers on the primary, Alembic migrations written expand/contract so deploys never lock tables, and point-in-time-recovery backups.
- **Users and audit:** `users`, `consents`, `saved_analyses`, and `llm_interactions` (inputs, prompt version, model, output, safety flags).
- **Only if you add portfolios, SIP mandates or orders:** an append-only double-entry `ledger_entries` table (rows in a transaction sum to zero, enforced by a deferred constraint trigger), an `idempotency_keys` table so retried requests cannot double-post, `SERIALIZABLE` isolation or `SELECT ... FOR UPDATE` on balance rows, and the outbox pattern for events. The repo has no transactions today; do not build this speculatively.
- **Vector indexing:** not needed now. If you add retrieval for the copilot (section 4.6), start with `pgvector` HNSW inside the same Postgres rather than a separate vector database.

### 3.5 Libraries, concurrency and patterns

| Replace | With | Why |
| --- | --- | --- |
| Pure-Python Monte Carlo loops | NumPy vectorised across paths; Numba `@njit` for path-dependent rules | I vectorised across paths and fixed the exit-day bug: 500 paths in 0.10 s versus 0.89 s (about 9x), and 20,000 paths x 10 years in 2.6 s \[RAN\]. Measure Numba before claiming more. |
| pandas loops over peers | Polars (lazy) for panel computations | Multi-core, no GIL for the heavy operations |
| Sync handlers with yfinance in the request path | Async FastAPI, `httpx.AsyncClient`, `anyio.to_thread` only for unavoidable blocking calls, CPU work in worker processes | The event loop never blocks |
| Raw dict responses | Pydantic v2 `response_model`s with bounded fields, `ORJSONResponse`, TS types generated with `openapi-typescript` | Documented, validated, no type drift |
| `uvicorn.run(app)` (one process) | Gunicorn with Uvicorn workers, or Granian, one worker per core behind the gateway | Uses all CPUs |
| Hand-rolled retries | `tenacity` with a breaker and `aiolimiter` | Backoff, jitter, bulkheads |
| Per-request `Groq(...)` | One async client, explicit timeouts, SSE streaming to the browser | Connection reuse, perceived latency |
| `useState` plus `fetch` | TanStack Query, or `AbortController` | Fixes the stale-response race |

Three small fixes you can apply this week. The CAGR exponent (`server.py:379`): `cagr = (final / initial) ** (252 / n_trading_days) - 1`. Bounded request model (`server.py:503`):

```python
Symbol = Annotated[str, StringConstraints(pattern=r"^[A-Z0-9&-]{1,20}$")]

class AnalyzeRequest(BaseModel):
    symbol: Symbol
    period_days: int = Field(365, ge=90, le=3650)
    sip_amount: float = Field(10_000, gt=0, le=1_000_000)
    sim_years: int = Field(10, ge=1, le=30)
    n_simulations: int = Field(1_000, ge=100, le=20_000)
```

And the stale-response race (`page.tsx:261`):

```ts
const ctrl = useRef<AbortController | null>(null);
const analyze = async (stock: StockInfo) => {
  ctrl.current?.abort();
  const c = (ctrl.current = new AbortController());
  setSelected(stock); setLoading(true); setResult(null); setError(null);
  try {
    const res = await fetch(`${API}/api/analyze`, { method: "POST", signal: c.signal,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol: stock.symbol }) });
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    setResult(await res.json());
  } catch (e) {
    if ((e as Error).name !== "AbortError") setError((e as Error).message);
  } finally {
    if (!c.signal.aborted) setLoading(false);
  }
};
```

## 4. Pillar 4: Advanced algorithms, quantitative models and ML

Ordering principle: **fix measurement before adding sophistication.** A fancier model on top of an invented metric is a fancier invented metric. Each item below replaces something I measured as broken in Pillar 2.

### 4.1 Behavior Gap, rebuilt on real flows

The defensible definition (Morningstar's "Mind the Gap" approach) is **time-weighted return minus dollar-weighted return** for a fund, where the dollar-weighted return reflects when investors actually put money in and took it out.

- **Math.** Fund NAV gives the period return `r_t`. Implied net flow in month `t` is `F_t = AUM_t - AUM_{t-1} * (1 + r_t)`. The dollar-weighted return is the IRR of the cash-flow series `{-F_t}` plus terminal AUM. `gap = TWR_annualised - IRR_annualised`.
- **Data.** AMFI publishes scheme-wise NAV and monthly AUM; both are public. For individual stocks there is no equivalent public flow series. Use proxies (NSE delivery percentage, FII/DII cash flows, shareholding-pattern retail share) and label them "flow-pressure indicators", never "investor return".
- **Uncertainty.** Block-bootstrap the monthly returns and flows to attach a confidence interval to every gap. Report "not distinguishable from zero" when that is true.
- **Personal mode (v2).** Import a consolidated account statement (CAS) or use the Account Aggregator framework to compute the user's own XIRR against the fund's TWR. That is a true personal behavior gap and a strong product story, with consent and data-protection obligations attached.
- **Libraries.** `numpy-financial` or `scipy.optimize.brentq` for IRR, `pandas`, `arch.bootstrap`.

### 4.2 Monte Carlo v2

The goal is a defensible answer to "how often does staying invested beat panic-exiting, and how sure are we?"

1. **Return generator.** Replace iid Normal with a **stationary block bootstrap** (Politis-Romano; `arch.bootstrap.StationaryBootstrap`) of 10 to 20 years of real returns. This preserves fat tails and volatility clustering without a parametric guess. Alternative: **GJR-GARCH(1,1) with Student-t innovations** (`arch`) and filtered historical simulation. For regime behavior, a 2 or 3 state Gaussian HMM (`hmmlearn`).
2. **Parameter uncertainty.** Draw the drift per path from a posterior shrunk toward a market-level prior (empirical Bayes), instead of fixing it at a noisy sample mean. This directly attacks the roughly 10-point drift standard error in section 2.2 and is the single most important change.
3. **Calibrated behavior model.** Replace "exit at -10%, wait 90 days" with an exit hazard `h(drawdown, vol)` estimated from observed investor behavior, for example AMFI's monthly SIP registration and closure counts and redemption data across drawdown regimes.
4. **Frictions.** STT, brokerage, exit load, capital-gains tax, and cash earning a liquid-fund yield rather than 0%.
5. **Paired design.** Use common random numbers (same path for both strategies) and report the distribution of paired differences. Report `P(SIP > panic)` with a Wilson or bootstrap interval, plus median and CVaR of terminal wealth for both. Seed, version and record everything.
6. **Performance.** Vectorise across paths (section 3.5). 20,000 paths took 2.6 s unoptimised \[RAN\], so 10,000-path runs fit comfortably in a worker.

### 4.3 From a heuristic panic score to a calibrated capitulation-risk model

Define the target first, because the current score has none. Pick one and justify it:

- **Regime label:** a high-volatility state from an HMM or a realised-volatility threshold, or
- **Event label:** "drawdown over X% followed by a Y% rebound within 10 trading days" (capitulation then recovery).

**Features** (all computed with lagged windows): log-volume robust z-score (median/MAD), **real delivery percentage** relative to its own 60-day history, India VIX level and change, Yang-Zhang realised volatility, downside semivariance, Amihud illiquidity, gap-down frequency, FII/DII net flow, sector-relative drawdown.

**Model.** Gradient-boosted trees (`lightgbm`) with monotone constraints so economically sensible directions are enforced, **SHAP** for a per-prediction "why this score", and **isotonic calibration** so "70" means roughly a 70% historical frequency. Add conformal intervals (`MAPIE`) and drift monitoring (PSI or KS on features).

**Validation (the part that earns credibility).** Purged and embargoed walk-forward cross-validation (López de Prado), because overlapping labels leak. Report PR-AUC and Brier score against two baselines: your current heuristic and a one-feature volume baseline. Then a cost-aware economic backtest. If the model does not beat the baselines out of sample, say so; an honest negative result is worth more than an unvalidated score.

**Anomaly and regime detection.** Bayesian online changepoint detection (Adams-MacKay) for volatility regime shifts, Isolation Forest on the multivariate feature vector, EWMA or CUSUM charts for online monitoring.

**A warning about forecasting.** Do not add LSTM or Transformer return forecasting for resume gloss. Daily return prediction has little exploitable signal, and an unvalidated forecaster is a credibility trap in a fintech interview. If you want forecasting, forecast **volatility** (HAR-RV, GARCH), which has demonstrated skill, and evaluate it with QLIKE loss.

**Fix the cheap defects regardless:** lagged window for the volume z-score, 52-week high for drawdown, Wilder smoothing for RSI (`avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()`), weighting recent days more than old ones.

### 4.4 Herding v2

- **Specification.** Keep the CCK regression, add the **Chiang-Zheng (2010)** forms: separate up-market and down-market regressions and extreme-day dummies. Add **quantile regression** of CSAD (`statsmodels` `QuantReg`) at upper quantiles, and the **Hwang-Salmon (2004)** state-space measure of herding toward the market using cross-sectional beta dispersion with a Kalman filter.
- **Inference.** One-sided test (`p = t.sf(t_stat, df)` when `gamma2 < 0`), with a **block or wild bootstrap** standard error. My simulations show HAC alone is over-sized at N=3 (11% false positives under the null) and the current two-sided test is under-powered, so a bootstrap plus a bigger cross-section is the real fix. Correct for multiple testing across sectors (Benjamini-Hochberg).
- **Cross-section.** NIFTY 500 sector groups with 20 or more names, value-weighted market return.
- **Reporting.** Replace the invented 0-100 "intensity" with the standardised `gamma2` (t-statistic) and a bootstrap interval. Present the result as a **sector** property, never a verdict about the selected stock.
- **Time variation.** Kalman time-varying `gamma2`, or a rolling window long enough for 3 parameters (at least 120 observations), instead of 30.
- **Test it.** Turn my null and power simulations into a permanent regression test (section 5.3).

### 4.5 News sentiment pipeline

- **Baseline model:** FinBERT (`ProsusAI/finbert`) exported to ONNX with int8 quantisation for CPU inference, or an LLM with a strict JSON schema validated by Pydantic (Groq JSON mode or `instructor`), replacing the greedy `\{.*\}` regex.
- **Pipeline:** parse feeds with `feedparser` or `defusedxml`, not regex; deduplicate near-identical stories (MinHash or embedding clustering) so one story is not counted ten times; weight by source quality; apply exponential time decay (a roughly one-day half-life).
- **Fallback lexicon:** word-boundary tokenisation with the Loughran-McDonald finance lexicon, which fixes the substring bug ("up" in "group").
- **Evaluation:** Financial PhraseBank plus a hand-labelled set of about 300 Indian headlines; report macro-F1. Add sentiment as a panic-model feature only if an ablation shows out-of-sample gain.

### 4.6 The copilot as a grounded, tool-using agent

- **Server-side context only.** The model calls typed tools (`get_panic(symbol)`, `get_herding(sector)`, `get_gap(fund)`) backed by your API and must cite their outputs. Never accept client-supplied context or roles.
- **Remove invitations to hallucinate.** Drop "real SIP success stories" and "historical examples", or ground them with retrieval over a curated, cited corpus (`pgvector` HNSW, citations required).
- **Guardrails.** A role allowlist, input length caps, an output classifier for directive advice ("you should buy/sell"), refusal templates, and per-user token budgets.
- **Evaluation in CI.** A golden prompt set plus adversarial prompt-injection cases, scored automatically; fail the build on regressions.
- **Engineering.** Stream responses (SSE), fix `temperature or self.temperature`, and add a fallback model plus a circuit breaker.

## 5. Pillar 5: Production infrastructure, observability and resume polish

### 5.1 Containers

Three images from one repo: `api`, `worker`, `web`. Multi-stage, non-root, pinned base images, healthchecks.

```dockerfile
# api / worker
FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev

FROM python:3.12-slim
RUN useradd -r -u 10001 app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
USER 10001
HEALTHCHECK CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/healthz')"
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000"]
```

For `web`, set `output: "standalone"` in `next.config.ts` and copy only `.next/standalone` into a distroless or alpine Node image. Remove Streamlit, Plotly, scikit-learn and beautifulsoup4 from the API image.

### 5.2 Kubernetes and zero-downtime deploys

- **Workloads:** `api` Deployment scaled by HPA on CPU and requests per second; `worker` Deployment scaled by **KEDA on Redis Stream lag**; a `CronJob` for end-of-day ingest and universe sync.
- **Safety:** readiness, liveness and startup probes (readiness fails if Postgres or Redis is unreachable); PodDisruptionBudgets; resource requests and limits; NetworkPolicies; `RollingUpdate` with `maxUnavailable: 0`, or **Argo Rollouts** canary with automated analysis against your SLO metrics.
- **Config and secrets:** External Secrets Operator backed by a cloud secrets manager; per-environment Groq keys with rotation; no secrets in images or Helm values.
- **Delivery:** Helm or Kustomize, **Argo CD** GitOps, Alembic migrations as a pre-deploy Job using expand/contract.
- **Be proportionate.** Use managed Postgres and Redis. For a portfolio demo, run the full manifests on `kind` or `k3d` in CI and deploy to a small managed cluster or a simpler platform. A cluster you cannot afford to keep up is worse than a clean Compose file plus tested manifests.

### 5.3 CI/CD and testing

| Stage | Tooling | What it proves |
| --- | --- | --- |
| Static | `ruff`, `pyright` or `mypy`, `eslint`, `tsc --noEmit` | Types and style |
| Unit | `pytest`, `hypothesis` | Analytics invariants: CAGR of constant growth equals that growth; scale invariance; Monte Carlo reproducible under a fixed seed |
| Statistical regression | `pytest` with seeded simulation | **Size and power of the herding test** (assert size at most 7% at N=20 and power at least 80% at a planted `gamma2`); the same harness I used here, turned into a test |
| Golden files | stored expected outputs | The CAGR and gap bugs can never silently return |
| Integration | `testcontainers` (Postgres, Redis), `respx` or `vcrpy` for provider fakes | Pipeline end to end |
| Contract | `schemathesis` against the OpenAPI schema | Bounds and error shapes hold under fuzzing |
| Chaos | `toxiproxy`: kill the provider, add latency | Outage yields `degraded`, never a verdict |
| Security | `pip-audit`, `npm audit`, `gitleaks`, `trivy`, CodeQL | Dependencies, secrets, images |
| Release | build, SBOM (`syft`), sign (`cosign`), Argo CD sync | Provenance |

**Load testing.** Use **k6** for HTTP (scenarios: 95% cached reads, 5% cold compute; ramp to 10,000 virtual users; a spike test; thresholds on p95 latency and error rate written into the script so CI fails on regression) and **Locust** for the chat flow with streaming. Run against a staging environment with a stubbed provider so you measure your system, not Yahoo. Publish the report in the repo. **That report is your evidence for any throughput claim.**

**Suggested SLOs:** p95 read latency under 300 ms; availability 99.9%; and a correctness SLO of **zero results served as `ok` while any input was degraded**.

### 5.4 Observability

- **Logs:** `structlog` JSON with `request_id`, `trace_id`, `instrument_id`, `data_version`; ship to Loki.
- **Traces:** OpenTelemetry SDK with FastAPI, `httpx`, SQLAlchemy and Redis instrumentation, through an OTel Collector to Tempo or Jaeger. Propagate trace context into worker jobs so one analysis is one trace across API, queue and worker.
- **Metrics:** Prometheus via `prometheus-fastapi-instrumentator` plus custom series: `provider_requests_total{provider,status}`, `provider_latency_seconds`, `circuit_breaker_state{provider}`, `analysis_degraded_total`, `cache_hit_ratio`, `stream_consumer_lag`, `llm_tokens_total`, `llm_errors_total`, `data_freshness_seconds{instrument}`.
- **Dashboards and alerts:** Grafana; multi-window SLO burn-rate alerts; alert on data freshness and on any non-zero count of ok-with-degraded-input.
- **Data quality:** `pandera` or Great Expectations checks on every ingest (freshness, missing sessions, split-like jumps, zero-volume runs); quarantine bad batches instead of computing on them.
- **Model monitoring:** PSI on features, calibration drift on the capitulation model, a weekly job that re-scores a held-out window.
- **Errors and synthetic checks:** Sentry on backend and frontend; a canary that requests a known symbol every minute and asserts `status == ok` and fresh `as_of`.

### 5.5 Prioritised, phased roadmap

Priorities: **P0** correctness and safety, **P1** foundations, **P2** scale and quant depth, **P3** polish. Each phase has an exit criterion you can demonstrate.

| Phase | Weeks | Work | Exit criterion |
| --- | --- | --- | --- |
| 0. Stop the bleeding (P0) | 1 | Add the `Result` envelope and suppress verdicts on degraded data. Fix the CAGR exponent, `intensity`, one-sided p-value, exit-day purchase, lagged z-score. Bound all request fields; role-allowlist chat; fix CORS to an explicit origin list. Fix the stale-response race and port mismatch. Pin dependencies. Delete duplicated logic by creating one shared `analytics` package. Rewrite README claims honestly. First tests (golden files for each bug). | Simulated Yahoo outage shows a degraded state and no verdict; all fixed bugs have a failing-then-passing test |
| 1. Foundations (P1) | 2 to 3 | Postgres + TimescaleDB schema, security master, provider abstraction, Redis cache with single-flight, async API, auth and rate limits, CI with lint, tests and security scans, Dockerfiles. | `docker compose up` runs the full stack; CI green; cache hit ratio visible |
| 2. Pipeline and scale (P2) | 4 to 6 | Redis Streams workers, EOD precompute, `202` job API, read replica and PgBouncer, k6 and Locust suites, first load-test report. | Documented load test with measured p95, throughput and error rate at the target concurrency |
| 3. Quant depth (P2) | 7 to 9 | Behavior gap on AMFI flows with bootstrap intervals; Monte Carlo v2 with block bootstrap and drift uncertainty; herding v2 with bootstrap inference on NIFTY 500 sectors; capitulation model with purged CV and honest baselines; notebooks that reproduce each result. | Each model ships with a validation notebook, baseline comparison and a statistical regression test |
| 4. Production (P2) | 10 to 12 | Kubernetes manifests, KEDA, Argo CD, OpenTelemetry, Grafana dashboards and SLO alerts, chaos tests, canary rollout, grounded copilot with eval suite. | Provider killed during load test: availability SLO holds and no `ok`-labelled degraded result |
| 5. Polish (P3) | ongoing | Architecture write-up, a short demo video, a public "what I got wrong" note covering the original bugs. | Repo readable cold in ten minutes |

The last item is not decoration. A candid before-and-after of real defects, found with evidence and fixed with tests, is more persuasive in an interview than a long list of technologies.

### 5.6 Resume bullets (XYZ format)

The numbers in brackets **must come from your own measurements** after you build the work: the k6 report, the CI results, the chaos run. Do not publish a figure you cannot reproduce in front of an interviewer. Also claim only what you personally built, given the team attribution in the README.

1. **Scale and performance.** "Re-architected a synchronous FastAPI monolith (about 15 serial upstream calls per request) into an event-driven pipeline (Redis Streams workers, TimescaleDB, Redis cache with single-flight), reducing p95 `/analyze` latency from \[measured baseline\] to \[X ms\] and sustaining \[N\] requests/s at \[10,000\] virtual users with \[Y\]% errors, verified by a k6 load-test report in the repo."
2. **Quantitative correctness.** "Audited the analytics layer against synthetic ground truth, finding and fixing \[N\] defects (a 48% CAGR overstatement, an unvalidated behavior-gap proxy, a mis-sided significance test), and replaced them with \[dollar- vs time-weighted return analysis on AMFI flows and a block-bootstrap Monte Carlo with parameter uncertainty\], guarded by \[M\] regression tests including size and power simulations of the herding test."
3. **Reliability, security and observability.** "Hardened a public fintech API (\[JWT auth, per-key rate limits, bounded inputs, circuit breakers\]) and instrumented it with OpenTelemetry, Prometheus and Grafana, eliminating silent-failure paths so provider outages surface as explicit degraded states; chaos tests that killed the market-data provider held \[99.X\]% availability with zero results served as healthy on stale inputs."

Bullet 2 is the most distinctive: very few portfolio projects can show they measured their own models' failure modes and published the corrections.

## Appendix: how the evidence was produced

All experiments import the repo's own `server.py` with I/O stubbed and run on synthetic data, so every number above is reproducible. The scripts accompany this document.

| Script | What it tests |
| --- | --- |
| `exp1.py` | Monte Carlo latency, reproducibility, drift sensitivity (first pass) |
| `exp2.py` | Monte Carlo win rate across a drift and volatility grid |
| `exp3.py` | Missing-Best-Days CAGR exponent; Behavior Gap formula on four scenarios |
| `exp4.py` to `exp7.py` | CCK herding detector: null size, power, and debugging of my own first planted-herding setup |
| `exp8.py` | Panic score base rate, z-score contamination, delivery proxy |
| `exp9.py` | Simulated Yahoo outage through `analyze()`, and the resulting frontend verdict |
| `exp10.py` | Vectorised Monte Carlo benchmark with the exit-day fix |

Known limits: synthetic data only, one data-generating process per test, and no live Yahoo calls. The frontend was read, not built. Treat the magnitudes as demonstrations of mechanism, and re-run them on real NSE history once your data layer exists.
