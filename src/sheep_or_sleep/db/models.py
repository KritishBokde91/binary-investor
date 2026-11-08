"""SQLAlchemy 2.0 models corresponding to AUDIT.md section 3.4 schema."""

import datetime
from typing import Any, Optional
from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    PrimaryKeyConstraint,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sheep_or_sleep.db.base import Base


class Instrument(Base):
    """Canonical security master entity."""
    __tablename__ = "instruments"

    instrument_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    isin: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    sector: Mapped[str] = mapped_column(String, nullable=False)
    listed_on: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    delisted_on: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)

    symbols: Mapped[list["InstrumentSymbol"]] = relationship(
        "InstrumentSymbol", back_populates="instrument", cascade="all, delete-orphan"
    )


class InstrumentSymbol(Base):
    """Historical and current symbol mapping for an instrument with validity dates."""
    __tablename__ = "instrument_symbols"

    instrument_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("instruments.instrument_id"), nullable=False
    )
    symbol: Mapped[str] = mapped_column(String, nullable=False)
    valid_from: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint("symbol", "valid_from"),
        Index("ix_instrument_symbols_lookup", "symbol", "valid_from", "valid_to"),
    )

    instrument: Mapped["Instrument"] = relationship("Instrument", back_populates="symbols")


class Bar1D(Base):
    """Daily OHLCV price and delivery bars (hypertable in TimescaleDB)."""
    __tablename__ = "bars_1d"

    instrument_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ts: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    open: Mapped[Optional[float]] = mapped_column(Numeric(14, 4), nullable=True)
    high: Mapped[Optional[float]] = mapped_column(Numeric(14, 4), nullable=True)
    low: Mapped[Optional[float]] = mapped_column(Numeric(14, 4), nullable=True)
    close: Mapped[Optional[float]] = mapped_column(Numeric(14, 4), nullable=True)
    volume: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    deliv_qty: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    adj_factor: Mapped[float] = mapped_column(Numeric(18, 10), nullable=False, server_default="1.0")
    source: Mapped[str] = mapped_column(String, nullable=False)
    ingested_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        PrimaryKeyConstraint("instrument_id", "ts"),
    )


class AnalysisResult(Base):
    """Versioned, append-only analysis results for auditability and caching."""
    __tablename__ = "analysis_results"

    instrument_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    params_hash: Mapped[str] = mapped_column(String, nullable=False)
    data_version: Mapped[str] = mapped_column(String, nullable=False)
    model_version: Mapped[str] = mapped_column(String, nullable=False)
    computed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint("instrument_id", "kind", "params_hash", "data_version"),
        Index("ix_analysis_results_time_lookup", "instrument_id", "kind", computed_at.desc()),
    )
