"""
Monte Carlo SIP vs. Panic Selling Simulator.
Compares:
1. Disciplined SIP: Invests monthly regardless of market conditions.
2. Panic Seller: Exits to cash on 10% drawdown from peak, waits 90 days.
"""

from __future__ import annotations
import numpy as np


def simulate_sip_vs_panic(
    sim_returns: np.ndarray | None = None,
    mean_r: float = 0.0005,
    std_r: float = 0.015,
    years: int = 10,
    sip: float = 10000.0,
    n_sims: int = 500,
) -> dict:
    """
    Run stochastic simulations comparing disciplined SIP vs panic-selling outcomes.
    """
    trading_days = 252 * years
    monthly = 21
    sip_results, panic_results = [], []

    for _ in range(n_sims):
        if sim_returns is not None:
            sim = sim_returns
        else:
            sim = np.random.normal(mean_r, std_r, trading_days)

        # 1. Disciplined SIP
        units, price = 0.0, 100.0
        for d in range(min(trading_days, len(sim))):
            price *= (1 + sim[d])
            price = max(price, 0.01)
            if d % monthly == 0:
                units += sip / price
        sip_results.append(units * price)

        # 2. Panic Seller
        units, cash, price, peak = 0.0, 0.0, 100.0, 100.0
        in_mkt, wait = True, 0
        for d in range(min(trading_days, len(sim))):
            price *= (1 + sim[d])
            price = max(price, 0.01)
            if in_mkt:
                peak = max(peak, price)
                if (price - peak) / peak <= -0.10:
                    cash += units * price
                    units = 0.0
                    in_mkt = False
                    wait = 90
                # Ordering fix: if exited today, monthly payment goes to cash, NOT units
                if in_mkt:
                    if d % monthly == 0:
                        units += sip / price
                else:
                    if d % monthly == 0:
                        cash += sip
            else:
                wait -= 1
                if d % monthly == 0:
                    cash += sip
                if wait <= 0:
                    in_mkt = True
                    peak = price
                    units += cash / price
                    cash = 0.0
        panic_results.append(units * price + cash)

    sip_arr = np.array(sip_results)
    panic_arr = np.array(panic_results)
    total_invested = sip * (trading_days // monthly)

    all_vals = np.concatenate([sip_arr, panic_arr])
    bin_min, bin_max = float(np.min(all_vals)), float(np.max(all_vals))
    n_bins = 30
    bin_edges = np.linspace(bin_min, bin_max, n_bins + 1)
    sip_hist, _ = np.histogram(sip_arr, bins=bin_edges)
    panic_hist, _ = np.histogram(panic_arr, bins=bin_edges)
    histogram = [
        {
            "binStart": round(float(bin_edges[i]), 0),
            "binEnd": round(float(bin_edges[i + 1]), 0),
            "sip": int(sip_hist[i]),
            "panic": int(panic_hist[i]),
        }
        for i in range(n_bins)
    ]

    mean_sip = float(np.mean(sip_arr))
    mean_panic = float(np.mean(panic_arr))

    return {
        "totalInvested": round(float(total_invested), 0),
        "years": years,
        "nSimulations": n_sims,
        "sip": {
            "mean": round(mean_sip, 0),
            "median": round(float(np.median(sip_arr)), 0),
            "p10": round(float(np.percentile(sip_arr, 10)), 0),
            "p90": round(float(np.percentile(sip_arr, 90)), 0),
        },
        "panic": {
            "mean": round(mean_panic, 0),
            "median": round(float(np.median(panic_arr)), 0),
            "p10": round(float(np.percentile(panic_arr, 10)), 0),
            "p90": round(float(np.percentile(panic_arr, 90)), 0),
        },
        "costOfPanic": {
            "meanLoss": round(float(mean_sip - mean_panic), 0),
            "pctLoss": round(float((mean_sip - mean_panic) / max(mean_sip, 1.0) * 100), 1),
            "winRate": round(float((sip_arr > panic_arr).sum() / len(sip_arr) * 100), 1),
        },
        "histogram": histogram,
    }
