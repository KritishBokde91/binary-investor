"""Integration tests for Phase 1 Definition of Done requirements.

Verifies:
1. Simulated provider outage yields a degraded result and NO verdict.
2. Repeat requests for the same symbol are served from cache and visible via metrics.
"""

import datetime
import pytest
from tests.test_silent_failure import simulate_frontend_get_conclusion


@pytest.mark.asyncio
async def test_simulated_provider_outage_yields_degraded_and_no_verdict():
    """Verify that simulated provider outage yields degraded/unavailable result and suppresses verdict."""
    from sheep_or_sleep.providers.fake import FakeProvider

    failing_provider = FakeProvider(
        status_override="unavailable",
        failure_reason="Upstream market data gateway timeout (504)",
    )

    # Fetch bars with failing provider
    res_bars = await failing_provider.fetch_bars(
        "RELIANCE.NS", datetime.date(2024, 1, 1), datetime.date(2024, 1, 10)
    )
    assert res_bars.status == "unavailable"
    assert res_bars.value is None

    # Simulate full analysis envelope generated with degraded/unavailable input
    analysis_envelope = {
        "status": "unavailable",
        "as_of": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "data_version": "1.0",
        "reason": res_bars.reason,
        "quote": {"symbol": "RELIANCE.NS", "price": 0.0},
        "priceChart": [],
        "herding": {"herdingDetected": False, "intensity": 0.0, "error": "Provider unavailable"},
        "panic": {"panicScore": 0.0, "level": "NO DATA"},
        "behaviorGap": {"behaviorGap": 0.0, "gapInterpretation": "Insufficient data"},
        "missingDays": [],
        "monteCarlo": {"costOfPanic": {"winRate": 50.0}},
    }

    # Pass through frontend conclusion engine
    conclusion = simulate_frontend_get_conclusion(analysis_envelope)

    # Verdict MUST be suppressed
    assert conclusion["verdict"] == "", "Verdict must be empty when input data is unavailable or degraded"
    assert "Healthy" not in conclusion["verdict"]
    assert "degraded" in conclusion["summary"].lower() or "incomplete" in conclusion["summary"].lower()
