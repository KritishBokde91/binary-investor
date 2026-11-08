# CHANGELOG-PHASE0.md: Phase 0 ("Stop the Bleeding") Implementation

*Repository: `SheepOrSleep` (`binary-investor`)*  
*Audit Reference: `Audit.md` section 5.5*  
*Execution Mode: Direct implementation on `master` branch as instructed by the user.*

---

## Summary of Completed Fixes

All Phase 0 items (a through k) were audited, confirmed in code, reproduced with failing tests first, fixed, and verified passing.

### Item a: Silent Failure & Degraded State Envelope
- **Audit Findings**: Finding 1, Section 2.1, Section 3.3.
- **Problem**: Upstream market data outages (e.g., Yahoo Finance 429/timeouts) previously returned HTTP 200 with zero-filled records (`price: 0`, `panicScore: 0`, empty history). The frontend `getConclusion()` interpreted the lack of warning flags as "Healthy Market Conditions... rational investor behavior."
- **Fix**:
  - Introduced typed result envelope fields in `server.py`: `status` (`ok`, `degraded`, `unavailable`), `as_of` (UTC ISO timestamp), `data_version` (`1.0`), and `reason`.
  - `/api/analyze` verifies that primary market data is present and non-zero; if upstream data fails, it raises `HTTPException(status_code=503)` with `status: "unavailable"`.
  - If secondary inputs (e.g. sector peers) fail or provide insufficient history, `status` is marked `"degraded"` with explanation in `reason`.
  - Updated `AnalysisResult` in `binary-investor/app/lib/types.ts`.
  - Hardened `getConclusion()` in `binary-investor/app/page.tsx`: requires all inputs to be verified OK (`status === "ok"`, `price > 0`, non-empty chart, non-error herding/panic/gap). If any input is degraded or unavailable, it suppresses the verdict (`verdict: ""`) and presents an explicit degraded data state.
- **Tests**:
  - `tests/test_silent_failure.py::test_yahoo_failure_does_not_return_200_zeros` (Failed on original code: returned 200 with 0 values; passes with 503).
  - `tests/test_silent_failure.py::test_frontend_get_conclusion_suppresses_verdict_when_inputs_not_ok` (Verified verdict suppression on degraded/zero data).
  - `tests/test_page_conclusion.test.mjs` (Node-based contract test on `page.tsx`).

### Item b: CAGR Exponent Bug in Missing-Best-Days
- **Audit Findings**: Finding 3, Section 1.2 row 67, Section 3.5.
- **Problem**: Both `server.py:379` and `analytics/behavior_gap.py:57-59` computed annualized CAGR as `** (365 / len(daily_returns))`. Because `len(daily_returns)` counts trading days (approx. 252/year), dividing calendar days (365) by trading days overstated CAGR by ~48% (a true 10.0% CAGR was calculated as ~14.86%).
- **Fix**:
  - Corrected exponent to `(252 / len(daily_returns))` in both `server.py` and `analytics/behavior_gap.py`.
- **Tests**:
  - `tests/test_cagr.py::test_cagr_constant_growth_series_in_server_and_behavior_gap` (Failed on original code: reported 14.8% on a 10.0% synthetic series; passes with 10.0%).

### Item c: Herding One-Sided p-Value & Non-Herding Zero Intensity
- **Audit Findings**: Finding Section 2.2 D, Section 4.4, Section 5.5.
- **Problem**: CCK regression tested the one-sided hypothesis $\gamma_2 < 0$ using a two-sided p-value (`2 * (1 - cdf)`), losing statistical power. Additionally, when herding was not detected (including anti-herding with $\gamma_2 > 0$), `intensity` reported `min(20, |gamma2| * 1000) > 0`, assigning positive "herding intensity" to anti-herding dispersion.
- **Fix**:
  - Replaced two-sided p-value with one-sided lower-tail p-value `float(stats.t.sf(-t_stat, df=n - k))` in `server.py` and `analytics/herd_detector.py`.
  - Ensured `intensity` strictly returns `0.0` whenever herding is not detected (`herdingDetected == False`).
- **Tests**:
  - `tests/test_herding.py::test_herding_non_herding_reports_zero_intensity` (Failed on original code: reported 20.0 intensity for $\gamma_2 > 0$; passes with 0.0).
  - `tests/test_herding.py::test_herding_one_sided_p_value_detects_herding_when_two_sided_misses` (Verified one-sided p-value computation using `t.sf`).

### Item d: Panic Seller Buys on Exit Day
- **Audit Findings**: Finding 1.3 #8, Section 3.5.
- **Problem**: In `server.py:420-421` and `analytics/portfolio_simulator.py:98-103, 201-204`, after triggering panic exit on monthly investment days (`in_mkt = False; units = 0`), the next line unconditionally executed `if d % monthly == 0: units += sip / price`, immediately rebuying stock units on the exit day.
- **Fix**:
  - Guarded monthly SIP purchases so that if the investor panicked and exited the market on day `d`, the contribution routes to cash (`cash += sip`) and `units` remains 0.
- **Tests**:
  - `tests/test_panic_exit.py::test_panic_seller_portfolio_immune_to_next_day_crash_after_exit` (Failed on original code: day 22 crash reduced panic seller's portfolio by 5,000 because stock units had been bought on day 21; passes with portfolio 100% in cash).

### Item e: Volume Z-Score Lagged Window
- **Audit Findings**: Finding 2.2 E, Section 3.5.
- **Problem**: In `server.py:261-262` and `analytics/panic_detector.py:38-40`, the 20-day rolling mean and standard deviation included today's volume. A massive volume spike contaminated its own baseline, creating a mathematical saturation ceiling at $\approx 4.25$ and compressing large spikes.
- **Fix**:
  - Shifted baseline window by 1 day (`Volume.shift(1).rolling(20)`) in both `server.py` and `analytics/panic_detector.py` to exclude today from its own mean and standard deviation.
- **Tests**:
  - `tests/test_panic_lagged_window.py::test_panic_volume_zscore_uses_lagged_window_excluding_today` (Failed on original code: 10-sigma volume spike produced z-score of 3.88; passes with > 6.0, registering ~9.8).

### Item f: Request Model Bounds, Symbol Validation & Chat Hardening
- **Audit Findings**: Finding 7, Section 2.3.
- **Problem**: Unbounded parameters (`simYears`, `nSimulations`), unvalidated `symbol` on endpoints, unbounded `/api/chat` accepting client-controlled roles (e.g. `system`) and appending client context to system prompts, and returning raw `str(e)` on errors leaking internals.
- **Fix**:
  - Added Pydantic field bounds to `AnalyzeRequest`: `periodDays` (90 to 3650), `sipAmount` (>0 to 1,000,000), `simYears` (1 to 30), `nSimulations` (100 to 20,000).
  - Validated symbol format with regex `^[A-Z0-9&.-]{1,20}$` and restricted to `KNOWN_SYMBOLS` (77 curated symbols); added validation to `get_quote` raising 400.
  - Hardened `ChatRequest`: restricted roles to `Literal["user", "assistant"]`, capped message content to 2,000 chars and total messages to 50.
  - Stopped accepting client-controlled context into the system prompt.
  - Replaced `return {"response": f"⚠️ Error: {e}"}` with generic `HTTPException(status_code=500, detail="An error occurred while processing the chat request.")` and 503 if missing API key.
- **Tests**:
  - `tests/test_request_validation.py::test_analyze_request_bounds_and_symbol_validation` (Verified 422 on out-of-bound inputs and unknown symbols).
  - `tests/test_request_validation.py::test_quote_endpoint_symbol_validation` (Verified 400 on unknown symbols).
  - `tests/test_request_validation.py::test_chat_role_allowlist_and_error_handling` (Verified 422 on invalid roles, 500 without internal error leak).

### Item g: CORS Origin Restriction & Credentials Off
- **Audit Findings**: Finding 8, Section 2.3.
- **Problem**: `server.py:27-33` used `allow_origins=["*"]` with `allow_credentials=True`, reflecting any calling origin (e.g. `https://evil.example`).
- **Fix**:
  - Configured `CORSMiddleware` with explicit origin list read from `ALLOWED_ORIGINS` / `CORS_ORIGINS` env vars (defaulting to `"http://localhost:3000,http://127.0.0.1:3000"`).
  - Set `allow_credentials=False`.
- **Tests**:
  - `tests/test_cors.py::test_cors_rejects_unauthorized_origins_and_disables_credentials` (Failed on original code: reflected `https://evil.example` with credentials; passes with unauthorized rejection and credentials disabled).

### Item h: Frontend Race in page.tsx analyze()
- **Audit Findings**: Finding 1.3 #2, Section 3.5.
- **Problem**: `analyze()` lacked cancellation. Fast successive clicks allowed earlier slower responses to overwrite newer results and cleared loading state prematurely.
- **Fix**:
  - Added `AbortController` ref in `DashboardPage` in `binary-investor/app/page.tsx`.
  - Aborted pending in-flight requests on new selection, passed `c.signal` to `fetch`.
  - Handled `AbortError` silently and guarded `setLoading(false)` with `if (!c.signal.aborted)`.
- **Tests**:
  - `tests/test_frontend_race.test.mjs` (Verified presence of `AbortController`, signal passing, and aborted loading state guard).

### Item i: Port & Environment Variable Consistency
- **Audit Findings**: Finding 1.1 line 58, Section 1.5.
- **Problem**: Mismatch between `server.py` (8000), `README.md` (8001), `copilot/page.tsx` (8001), `page.tsx` (8000), and `AICopilot.tsx` (8000).
- **Fix**:
  - Standardized on default port `8000` across all files.
  - Backend reads `PORT` env var (defaulting to 8000).
  - Frontend components (`page.tsx`, `AICopilot.tsx`, `copilot/page.tsx`) consistently use `process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"`.
  - Replaced all 8001 occurrences in `README.md` with 8000.
- **Tests**:
  - `tests/test_port_consistency.test.mjs` (Automated verification across all 5 files).

### Item j: Python Dependencies Pinned & Unused Removed
- **Audit Findings**: Finding 1.2 row 79, Section 2.3.
- **Problem**: `requirements.txt` contained unpinned dependencies and unused libraries (`scikit-learn`, `beautifulsoup4`).
- **Fix**:
  - Verified no file in `server.py`, `app.py`, `analytics/`, `ai/`, `config/`, `data/`, `pages/`, or `ui/` imports `sklearn` or `bs4`.
  - Removed `scikit-learn` and `beautifulsoup4`.
  - Pinned all remaining dependencies to exact installed versions.
- **Tests**:
  - `tests/test_requirements.py::test_requirements_pinned_and_unused_removed`.

### Item k: Corrected README Claims
- **Audit Findings**: Section 1.5, Section 0.
- **Problem**: Discrepancies between claims in `README.md` and repository reality.
- **Fix**:
  - Removed "production-ready" claim (labeled as educational full-stack prototype).
  - Clarified "Investor CAGR" and "Behavior Gap" as heuristic proxy models based on volume-price correlation rather than actual brokerage flow data.
  - Corrected panic drawdown description to "high of analysis window (90-180 days)" instead of 52-week high.
  - Corrected delivery pressure description to "Intraday Range Ratio proxy".
  - Updated Recharts dependency in table to `^3.8.0` (matching `package.json`).
  - Removed non-existent `tailwind.config.ts` from project structure tree.
  - Corrected repository clone URL from hackathon repository to `KritishBokde91/binary-investor`.
- **Tests**:
  - `tests/test_readme_claims.test.mjs`.

---

## Test Verification Summary

- **Pytest test suite**: 12 passed in 1.77s (`tests/test_*.py`)
- **Node test suite**: 4 passed (`tests/*.test.mjs`)
- **Total tests**: 16 passed, 0 failed.
- **Skipped / Not Reproducible**: None. Every finding cited in Section 1.5 & Section 5.5 was confirmed in code, reproduced with failing tests, and resolved.
