import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch

import server
from analytics.portfolio_simulator import PortfolioSimulator


def test_panic_seller_portfolio_immune_to_next_day_crash_after_exit():
    """
    AUDIT.md Finding 1.3 #8 & Phase 0 Item d:
    If panic selling is triggered on day 21 (a monthly SIP day),
    the seller exits and the SIP goes to cash.
    If day 22 crashes by 50%, the panic seller should be in 100% cash,
    so day 22 returns must NOT reduce the panic seller's wealth.

    Under the bug:
      units += sip / price was executed on day 21 after in_mkt = False,
      so the seller held stock units on day 22 and lost money on day 22!
    """
    trading_days = 252 * 1
    # Day 0: SIP buys at price 100
    # Day 21: price drops 15%, panic exit triggers, and it's a monthly day (d=21)
    # Day 22: price drops 50%
    # Days 23+: returns are 0
    sim = np.zeros(trading_days)
    sim[21] = -0.15  # Day 21 crash triggers exit
    sim[22] = -0.50  # Day 22 massive crash

    # Run server.simulate_sip_vs_panic
    with patch("server.fetch_historical", return_value=pd.DataFrame({"Returns": [0.001]*100})), \
         patch("numpy.random.normal", return_value=sim):
        res = server.simulate_sip_vs_panic("TEST.NS", years=1, sip=10000, n_sims=1)
        panic_val = res["panic"]["median"]

    # Price at day 0 = 100. SIP buys 100 units (10000 / 100).
    # Day 1-20: price 100.
    # Day 21: price drops to 85.
    # On day 21, drawdown is (85-100)/100 = -15% <= -10%. Panic exit triggers!
    # All 100 units sold at 85 = 8500 cash.
    # Day 21 SIP (10000): should go to CASH!
    # Expected total cash on day 21 = 8500 + 10000 = 18500.
    # Days 22-41: wait drops, days 42+: monthly cash adds.
    # Total monthly days in 252 days: d = 0, 21, 42, 63, 84, 105, 126, 147, 168, 189, 210, 231, 252 (12 or 13 buys).
    # Crucially, under the bug, units were bought on day 21: units = 10000 / 85 = 117.65.
    # Then on day 22, price dropped 50% to 42.5! Those units lost 5000 in value!
    # If the bug exists, panic_val is ~5000 lower than if units were 0.

    # Compute expected panic value when units == 0 on day 21:
    units, cash, price, peak = 0.0, 0.0, 100.0, 100.0
    in_mkt, wait = True, 0
    monthly = 21
    for d in range(trading_days):
        price *= (1 + sim[d])
        price = max(price, 0.01)
        if in_mkt:
            peak = max(peak, price)
            if (price - peak) / peak <= -0.10:
                cash += units * price
                units = 0
                in_mkt = False
                wait = 90
            if in_mkt:
                if d % monthly == 0:
                    units += 10000 / price
            else:
                if d % monthly == 0:
                    cash += 10000
        else:
            wait -= 1
            if d % monthly == 0:
                cash += 10000
            if wait <= 0:
                in_mkt = True
                peak = price
                units += cash / price
                cash = 0
    expected_fixed_panic = units * price + cash

    assert np.isclose(panic_val, expected_fixed_panic, atol=1.0), (
        f"Panic seller bought units on exit day! Got {panic_val}, expected {expected_fixed_panic}"
    )
