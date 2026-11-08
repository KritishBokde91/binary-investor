"""Tests for Database Schema, Models, and Universe Seeding (Phase 1 Step 2)."""

import datetime
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


@pytest.mark.asyncio
async def test_models_and_schema_initialization():
    """Verify models import and create tables cleanly."""
    from sheep_or_sleep.db.base import Base
    from sheep_or_sleep.db.models import Instrument, InstrumentSymbol, Bar1D, AnalysisResult

    # In-memory async SQLite engine for quick schema test
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    assert Instrument.__tablename__ == "instruments"
    assert InstrumentSymbol.__tablename__ == "instrument_symbols"
    assert Bar1D.__tablename__ == "bars_1d"
    assert AnalysisResult.__tablename__ == "analysis_results"
    await engine.dispose()


@pytest.mark.asyncio
async def test_seed_universe_and_symbol_renames():
    """Verify seed_universe populates instruments and maps historical renames properly."""
    from sheep_or_sleep.db.base import Base
    from sheep_or_sleep.db.models import Instrument, InstrumentSymbol
    from sheep_or_sleep.db.seed import seed_universe, resolve_instrument_by_symbol

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        count = await seed_universe(session)
        assert count == 77

        # Total instruments
        result = await session.execute(select(Instrument))
        instruments = result.scalars().all()
        assert len(instruments) == 77

        # Verify Zomato -> Eternal resolution
        # Before 2025-04-09, ZOMATO was active
        inst_zomato = await resolve_instrument_by_symbol(
            session, "ZOMATO.NS", as_of=datetime.date(2024, 1, 15)
        )
        assert inst_zomato is not None

        # After 2025-04-09, ETERNAL is active
        inst_eternal = await resolve_instrument_by_symbol(
            session, "ETERNAL.NS", as_of=datetime.date(2025, 5, 1)
        )
        assert inst_eternal is not None
        assert inst_zomato.instrument_id == inst_eternal.instrument_id
        assert inst_eternal.isin == "INE758T01015"

        # Verify Tata Motors -> TMPV resolution
        # Before 2025-10-24, TATAMOTORS was active
        inst_tm = await resolve_instrument_by_symbol(
            session, "TATAMOTORS.NS", as_of=datetime.date(2024, 1, 15)
        )
        assert inst_tm is not None

        # On or after 2025-10-24, TMPV is active
        inst_tmpv = await resolve_instrument_by_symbol(
            session, "TMPV.NS", as_of=datetime.date(2025, 11, 1)
        )
        assert inst_tmpv is not None
        assert inst_tm.instrument_id == inst_tmpv.instrument_id
        assert inst_tmpv.isin == "INE155A01022"

    await engine.dispose()


@pytest.mark.asyncio
async def test_bars_and_analysis_results_storage():
    """Verify bars_1d and analysis_results record insertion and constraints."""
    from sheep_or_sleep.db.base import Base
    from sheep_or_sleep.db.models import Bar1D, AnalysisResult

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        bar = Bar1D(
            instrument_id=1,
            ts=datetime.date(2024, 1, 2),
            open=100.0,
            high=105.0,
            low=99.0,
            close=104.5,
            volume=500000,
            deliv_qty=250000,
            adj_factor=1.0,
            source="yfinance",
        )
        session.add(bar)

        analysis = AnalysisResult(
            instrument_id=1,
            kind="panic_score",
            params_hash="default_v1",
            data_version="2024-01-02",
            model_version="1.0.0",
            payload={"panic_score": 12.5, "status": "ok"},
        )
        session.add(analysis)
        await session.commit()

        # Query back
        res_bar = await session.get(Bar1D, (1, datetime.date(2024, 1, 2)))
        assert res_bar is not None
        assert float(res_bar.close) == 104.5

        res_analysis = await session.get(
            AnalysisResult, (1, "panic_score", "default_v1", "2024-01-02")
        )
        assert res_analysis is not None
        assert res_analysis.payload["panic_score"] == 12.5

    await engine.dispose()


def test_alembic_migration_sql_generation(capsys):
    """Verify that Alembic runs offline SQL generation successfully and includes hypertable."""
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head", sql=True)
    captured = capsys.readouterr()
    generated_sql = captured.out

    assert "CREATE TABLE instruments" in generated_sql
    assert "CREATE TABLE instrument_symbols" in generated_sql
    assert "CREATE TABLE bars_1d" in generated_sql
    assert "CREATE TABLE analysis_results" in generated_sql
    assert "create_hypertable('bars_1d'" in generated_sql

