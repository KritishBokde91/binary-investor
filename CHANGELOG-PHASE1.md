# Phase 1: Foundations — Changelog

This changelog records the complete implementation of **Phase 1 ("Foundations")** of the SheepOrSleep (binary-investor) engineering upgrade, following the approved step-by-step roadmap and AUDIT.md architectural specifications.

---

## Step 0: Plan & Architecture Review
- Outlined explicit layout and dependencies: Python 3.12+, FastAPI async, SQLAlchemy 2.0 async + asyncpg, Alembic, Redis 7, TimescaleDB, Pydantic v2.
- Confirmed test-first workflow and strict separation between dev-only providers (yfinance) and test doubles (`FakeProvider`, `fakeredis`).

---

## Step 1: Pure Shared Analytics Package
- **Objective**: Move analytics logic (CCK herding, panic score, behavior gap, missing best days, Monte Carlo SIP simulation) into an isolated, importable package.
- **Changes**:
  - Created pure library modules:
    - `src/sheep_or_sleep/analytics/herding.py`: CCK (2000) OLS regression with one-sided p-values.
    - `src/sheep_or_sleep/analytics/panic.py`: Multi-factor panic score with lagged 20-day rolling volume windows.
    - `src/sheep_or_sleep/analytics/behavior_gap.py`: Correlation-based behavioral drag and missing days calculation with 252-day CAGR exponent.
    - `src/sheep_or_sleep/analytics/simulator.py`: Monte Carlo simulation with fixed exit-day SIP cash routing.
  - Deleted ~270 lines of duplicated analytics from `server.py` and delegated execution to `sheep_or_sleep.analytics`.
  - Replaced legacy formulas in `analytics/behavior_gap.py` to delegate to `_shared_compute_missing_days`.
- **Tests**:
  - Authored `tests/test_shared_analytics.py` (4 unit tests covering all mathematical functions).
- **Status**: Passed.

---

## Step 2: Database, Migrations & Security Master Seeding
- **Objective**: Provision Postgres 16 with TimescaleDB, Alembic async migrations for the schema in AUDIT.md section 3.4, and seed the 77-stock universe with historical ticker renames.
- **Verified Ticker Renames**:
  - `ZOMATO` $\to$ `ETERNAL`: Verified via NSE Circular `NSE/CML/67420` (Effective April 09, 2025). Mapped to canonical ISIN `INE758T01015`.
  - `TATAMOTORS` $\to$ `TMPV`: Verified via NSE Circular `NSE/CML/70875` (Effective October 24, 2025). Mapped to canonical ISIN `INE155A01022`.
- **Changes**:
  - Configured `docker-compose.yml` with `timescale/timescaledb:latest-pg16` (healthcheck via `pg_isready`).
  - Authored SQLAlchemy 2.0 async engine and declarative base in `src/sheep_or_sleep/db/base.py`.
  - Authored models in `src/sheep_or_sleep/db/models.py`:
    - `Instrument` (`instruments`): `instrument_id`, `isin` (UNIQUE), `name`, `sector`, `listed_on`, `delisted_on`.
    - `InstrumentSymbol` (`instrument_symbols`): `instrument_id`, `symbol`, `valid_from`, `valid_to`, `PK(symbol, valid_from)`.
    - `Bar1D` (`bars_1d`): `instrument_id`, `ts`, `open`, `high`, `low`, `close`, `volume`, `deliv_qty`, `adj_factor`, `source`, `ingested_at`, `PK(instrument_id, ts)`.
    - `AnalysisResult` (`analysis_results`): `instrument_id`, `kind`, `params_hash`, `data_version`, `model_version`, `computed_at`, `payload` (JSONB), `PK(instrument_id, kind, params_hash, data_version)`, index on `(instrument_id, kind, computed_at DESC)`.
  - Initialized Alembic (`alembic.ini`, `alembic/env.py`) and created revision `0001_initial_schema.py` creating tables and setting up TimescaleDB hypertable (`SELECT create_hypertable('bars_1d', 'ts', chunk_time_interval => INTERVAL '1 year', if_not_exists => TRUE);`).
  - Authored `src/sheep_or_sleep/db/seed.py`: Idempotently seeds all 77 stocks from `server.STOCK_UNIVERSE` with date-bounded symbol mapping.
- **Tests**:
  - Authored `tests/test_db_schema.py` (4 tests: model creation, seed resolution by historical date, bar/result storage, and Alembic offline SQL generation).
- **Status**: Passed.

---

## Step 3: Market Data Provider Layer
- **Objective**: Implement `MarketDataProvider` Protocol, `FakeProvider`, `YFinanceProvider` with circuit breaker and tenacity retries, returning standard `Result[T]` envelopes and persisting bars.
- **Changes**:
  - Authored `src/sheep_or_sleep/providers/envelope.py`: Generic Pydantic `Result[T]` with `status`, `as_of`, `data_version`, `value`, `reason`.
  - Authored `src/sheep_or_sleep/providers/circuit_breaker.py`: Async 3-state circuit breaker (`CLOSED`, `OPEN`, `HALF_OPEN`) with fast failure on open cooldown.
  - Authored `src/sheep_or_sleep/providers/base.py`: Protocol definition and idempotent `persist_bars` upsert helper.
  - Authored `src/sheep_or_sleep/providers/fake.py`: In-memory deterministic provider with configurable error modes.
  - Authored `src/sheep_or_sleep/providers/yfinance.py`: Explicitly marked `development only`, offloads blocking calls via `asyncio.to_thread` with timeouts, tenacity backoff jitter (`wait_exponential_jitter`), and circuit breaker wrapping.
- **Tests**:
  - Authored `tests/test_market_provider.py` (5 tests covering envelope semantics, circuit breaker transitions, bar DB persistence, dev-only metadata, and error handling).
- **Status**: Passed.

---

## Step 4: Redis Cache & Concurrency
- **Objective**: Implement async Redis cache with single-flight locking (`SET NX PX`), stale-while-revalidate, and hit/miss observability.
- **Changes**:
  - Authored `src/sheep_or_sleep/cache/client.py`: Async connection manager using `redis.asyncio`.
  - Authored `src/sheep_or_sleep/cache/service.py`:
    - Dogpile stampede prevention: Distributed lock `lock:{key}` with token verification Lua release script.
    - Stale-while-revalidate: Returns stale data instantly while revalidating in background with single-flight coordination.
    - Observability: Exposes `hits`, `misses`, `stale_hits`, `stampedes_prevented`, and `hit_ratio`.
    - Resilient fallback when Redis is unreachable.
- **Tests**:
  - Authored `tests/test_redis_cache.py` (4 tests: hit/miss ratio, 10-way concurrent request stampede protection, background revalidation, and raw get/set/reset).
- **Status**: Passed.

---

## Step 5: Async API Handlers & Observability
- **Objective**: Convert `server.py` to async handlers reading from Postgres/Redis, add `/healthz`, `/readyz`, `/api/metrics`, rate limiting, auth scaffold, and Pydantic response models.
- **Changes**:
  - Authored `src/sheep_or_sleep/api/schemas.py`: Pydantic response models for all routes.
  - Authored `src/sheep_or_sleep/api/auth.py`: API key (`X-API-Key`) and JWT Bearer token authentication dependency.
  - Authored `src/sheep_or_sleep/api/rate_limiter.py`: Sliding-window rate limiter per client IP / API key backed by Redis.
  - Updated `server.py`:
    - Converted all route handlers to `async def`.
    - Added `GET /healthz` (liveness probe).
    - Added `GET /readyz` (readiness probe: tests Postgres `SELECT 1` and Redis `PING`; returns HTTP 503 if either is down).
    - Added `GET /api/metrics` (telemetry endpoint exposing cache hits, misses, and hit ratio).
    - Added Redis caching to `/api/quote` and `/api/analyze`.
    - Added `response_model` across all endpoints.
- **Tests**:
  - Authored `tests/test_api_async.py` (6 tests: liveness, healthy/unhealthy readiness, metrics, rate limiting, auth, and cache serving).
- **Status**: Passed.

---

## Step 6: Containers & Docker Compose
- **Objective**: Multi-stage Dockerfiles for API and web, non-root execution, healthchecks, pinned base images, and full stack orchestration in `docker-compose.yml`.
- **Changes**:
  - Authored `Dockerfile.api`: Pinned `python:3.12-slim` builder stage, non-root user `app` (`UID 10001`), `/healthz` HTTP healthcheck.
  - Authored `binary-investor/Dockerfile`: Pinned `node:20-alpine` multi-stage build, `output: "standalone"` enabled in `next.config.ts`, non-root user `nextjs` (`UID 1001`), port 3000 healthcheck.
  - Updated `docker-compose.yml`: Coordinates `postgres`, `redis`, `api`, and `web` with environment variables, networks, and dependency ordering via `service_healthy`.
- **Tests**:
  - Authored `tests/test_containers.py` (3 tests verifying multi-stage build, non-root users, healthchecks, and compose services).
- **Status**: Passed.

---

## Step 7: CI Pipeline & End-to-End Verification
- **Objective**: GitHub Actions workflow running ruff, mypy, pytest with Postgres+Redis service containers, eslint, tsc, Next.js build, pip-audit, and gitleaks.
- **Changes**:
  - Authored `.github/workflows/ci.yml`:
    - Backend CI job with Postgres (TimescaleDB) and Redis 7 service containers, running Ruff, Mypy, pip-audit, and Pytest.
    - Frontend CI job running ESLint, TypeScript compiler check (`npx tsc --noEmit`), Next.js standalone build, and Node contract tests.
    - Security CI job with pinned `gitleaks/gitleaks-action@v2` secret scanning.
  - Authored `tests/test_integration_phase1.py`: Verifies end-to-end simulated provider outage with `FakeProvider(status_override="unavailable")` yielding a degraded result and suppressing verdict rendering.
- **Tests**:
  - `tests/test_ci_workflow.py`: Validates CI structure, pinned actions, service containers, and toolchain steps.
  - `tests/test_integration_phase1.py`: Validates end-to-end provider outage behavior.
- **Status**: Passed.

---

## Final Verification Summary
```
Pytest Suite:  40 passed, 1 warning (100%)
Node.js Tests:  4 passed (100%)
Total:         44 automated tests passing
```
All criteria for **Phase 1 ("Foundations")** are fulfilled and verified.
