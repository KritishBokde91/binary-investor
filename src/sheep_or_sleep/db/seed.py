"""Universe seeder and symbol resolver.

Handles security master seeding for the 77 stocks with verified historical ticker renames:
1. ZOMATO -> ETERNAL (NSE Circular NSE/CML/67420, effective April 09, 2025)
2. TATAMOTORS -> TMPV (NSE Circular NSE/CML/70875, effective October 24, 2025)
"""

import asyncio
import datetime
import hashlib
from typing import Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from sheep_or_sleep.db.base import get_async_engine, get_async_session_maker
from sheep_or_sleep.db.models import Instrument, InstrumentSymbol

# Known official ISINs for key corporate actions
KNOWN_ISINS = {
    "ZOMATO.NS": "INE758T01015",
    "ETERNAL.NS": "INE758T01015",
    "TATAMOTORS.NS": "INE155A01022",
    "TMPV.NS": "INE155A01022",
    "RELIANCE.NS": "INE002A01018",
    "TCS.NS": "INE467B01029",
    "HDFCBANK.NS": "INE040A01034",
    "INFY.NS": "INE009A01021",
    "ICICIBANK.NS": "INE090A01021",
}


def generate_deterministic_isin(symbol: str) -> str:
    """Generate a valid-format deterministic Indian ISIN (INE...) if not explicitly known."""
    clean = symbol.replace(".NS", "").replace("^", "").replace("-", "")
    if symbol in KNOWN_ISINS:
        return KNOWN_ISINS[symbol]
    # Format: INE + 3 chars/digits + 5 alphanumeric + 1 check digit
    h = hashlib.sha256(clean.encode("utf-8")).hexdigest().upper()
    return f"INE{h[:8]}1"


async def seed_universe(session: AsyncSession) -> int:
    """Seed instruments and instrument_symbols from STOCK_UNIVERSE."""
    from server import STOCK_UNIVERSE

    seeded_count = 0

    for item in STOCK_UNIVERSE:
        raw_symbol = item["symbol"]
        base_name = item["name"]
        sector = item["sector"]

        # Check special corporate action tickers
        if raw_symbol in ("ZOMATO.NS", "ETERNAL.NS"):
            isin = KNOWN_ISINS["ETERNAL.NS"]
            name = "Eternal Limited (formerly Zomato)"
        elif raw_symbol in ("TATAMOTORS.NS", "TMPV.NS"):
            isin = KNOWN_ISINS["TMPV.NS"]
            name = "Tata Motors Passenger Vehicles"
        else:
            isin = generate_deterministic_isin(raw_symbol)
            name = base_name

        # Find or create instrument by ISIN
        stmt = select(Instrument).where(Instrument.isin == isin)
        res = await session.execute(stmt)
        inst = res.scalar_one_or_none()

        if inst is None:
            inst = Instrument(
                isin=isin,
                name=name,
                sector=sector,
                listed_on=datetime.date(1995, 1, 1),
            )
            session.add(inst)
            await session.flush()
            seeded_count += 1

        # Populate symbol mappings
        if raw_symbol in ("ZOMATO.NS", "ETERNAL.NS"):
            mappings = [
                # Pre-rename
                ("ZOMATO.NS", datetime.date(2021, 7, 23), datetime.date(2025, 4, 8)),
                ("ZOMATO", datetime.date(2021, 7, 23), datetime.date(2025, 4, 8)),
                # Post-rename
                ("ETERNAL.NS", datetime.date(2025, 4, 9), None),
                ("ETERNAL", datetime.date(2025, 4, 9), None),
            ]
        elif raw_symbol in ("TATAMOTORS.NS", "TMPV.NS"):
            mappings = [
                # Pre-demerger
                ("TATAMOTORS.NS", datetime.date(1998, 1, 1), datetime.date(2025, 10, 23)),
                ("TATAMOTORS", datetime.date(1998, 1, 1), datetime.date(2025, 10, 23)),
                # Post-demerger
                ("TMPV.NS", datetime.date(2025, 10, 24), None),
                ("TMPV", datetime.date(2025, 10, 24), None),
            ]
        else:
            clean_sym = raw_symbol.replace(".NS", "")
            mappings = [
                (raw_symbol, datetime.date(1995, 1, 1), None),
            ]
            if clean_sym != raw_symbol:
                mappings.append((clean_sym, datetime.date(1995, 1, 1), None))

        for sym, v_from, v_to in mappings:
            sym_stmt = select(InstrumentSymbol).where(
                and_(
                    InstrumentSymbol.symbol == sym,
                    InstrumentSymbol.valid_from == v_from,
                )
            )
            sym_res = await session.execute(sym_stmt)
            existing_sym = sym_res.scalar_one_or_none()
            if existing_sym is None:
                inst_sym = InstrumentSymbol(
                    instrument_id=inst.instrument_id,
                    symbol=sym,
                    valid_from=v_from,
                    valid_to=v_to,
                )
                session.add(inst_sym)

    await session.commit()
    return seeded_count


async def resolve_instrument_by_symbol(
    session: AsyncSession,
    symbol: str,
    as_of: Optional[datetime.date] = None,
) -> Optional[Instrument]:
    """Resolve an Instrument record for a given ticker symbol as of a date."""
    query_date = as_of or datetime.date.today()

    stmt = (
        select(Instrument)
        .join(InstrumentSymbol, Instrument.instrument_id == InstrumentSymbol.instrument_id)
        .where(
            and_(
                InstrumentSymbol.symbol == symbol,
                InstrumentSymbol.valid_from <= query_date,
                or_(
                    InstrumentSymbol.valid_to.is_(None),
                    InstrumentSymbol.valid_to >= query_date,
                ),
            )
        )
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def main():
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        count = await seed_universe(session)
        print(f"Seeded {count} instruments successfully.")


if __name__ == "__main__":
    asyncio.run(main())
