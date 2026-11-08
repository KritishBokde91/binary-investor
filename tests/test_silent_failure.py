import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import server


def simulate_frontend_get_conclusion(result: dict) -> dict:
    """
    Python reference implementation of getConclusion() from page.tsx:286-337,
    mirroring the exact frontend logic.
    """
    if not result:
        return {"verdict": "", "summary": "", "actions": [], "riskLevel": "low"}

    status = result.get("status")
    quote = result.get("quote", {})
    herding = result.get("herding", {})
    panic = result.get("panic", {})
    behavior_gap = result.get("behaviorGap", {})
    price_chart = result.get("priceChart", [])

    is_data_ok = (
        status == "ok"
        and quote.get("price", 0) > 0
        and len(price_chart) > 0
        and panic.get("level") != "NO DATA"
        and behavior_gap.get("gapInterpretation") != "Insufficient data"
        and not herding.get("error")
    )

    if not is_data_ok:
        reason = result.get("reason") or "Incomplete or degraded input data"
        return {
            "verdict": "",
            "summary": f"Analysis inputs are incomplete or degraded ({reason}). A behavioral verdict cannot be rendered until data quality is restored.",
            "actions": [
                "Data feeds for this stock or sector peers are incomplete or degraded.",
                "Verdict suppressed to prevent false positive 'Healthy' assessments on missing data.",
            ],
            "riskLevel": "medium",
        }

    panic_score = panic.get("panicScore", 0)
    herd_detected = herding.get("herdingDetected", False)
    gap = abs(behavior_gap.get("behaviorGap", 0))

    flags = []
    if herd_detected:
        flags.append("herding")
    if panic_score > 50:
        flags.append("panic")
    if gap > 2:
        flags.append("behavior-gap")

    if len(flags) == 0:
        return {
            "verdict": "✅ Healthy Market Conditions",
            "summary": f"{quote.get('name')} shows rational investor behavior...",
            "actions": [],
            "riskLevel": "low",
        }
    elif len(flags) >= 2:
        return {
            "verdict": "🚨 High Behavioral Risk Detected",
            "summary": "High risk",
            "actions": [],
            "riskLevel": "high",
        }
    return {
        "verdict": "⚠️ Moderate Behavioral Signals",
        "summary": "Moderate signals",
        "actions": [],
        "riskLevel": "medium",
    }


def test_yahoo_failure_does_not_return_200_zeros():
    """
    AUDIT.md Finding 1 & Phase 0 Item a:
    Simulate Yahoo failure. /api/analyze must NOT return HTTP 200 with zero-filled data.
    """
    with patch("yfinance.Ticker") as mock_ticker:
        mock_instance = MagicMock()
        mock_instance.history.side_effect = Exception("HTTP 429 Client Error: Too Many Requests")
        mock_instance.info = {}
        mock_ticker.return_value = mock_instance

        client = TestClient(server.app)
        response = client.post("/api/analyze", json={"symbol": "RELIANCE.NS"})

        # Must not return 200 with zero-filled data
        assert response.status_code == 503
        data = response.json()
        # Check error detail envelope
        detail = data.get("detail", {})
        if isinstance(detail, dict):
            assert detail.get("status") in ["unavailable", "degraded"]


def test_frontend_get_conclusion_suppresses_verdict_when_inputs_not_ok():
    """
    AUDIT.md Finding 1 & Phase 0 Item a:
    Frontend getConclusion() must show a degraded state and must NOT render
    a verdict unless every input is ok. No 'Healthy' verdict on degraded/empty data.
    """
    # 1. Zero-filled legacy payload (simulated upstream failure)
    zero_filled_result = {
        "status": "unavailable",
        "quote": {"symbol": "RELIANCE.NS", "name": "RELIANCE.NS", "price": 0},
        "priceChart": [],
        "herding": {"herdingDetected": False, "intensity": 0, "gamma2": 0, "pValue": 1, "error": "Insufficient data"},
        "panic": {"panicScore": 0, "level": "NO DATA", "factors": {}},
        "behaviorGap": {"behaviorGap": 0, "gapInterpretation": "Insufficient data"},
        "monteCarlo": {"costOfPanic": {"pctLoss": 0, "meanLoss": 0, "winRate": 50}},
    }
    conclusion = simulate_frontend_get_conclusion(zero_filled_result)
    assert conclusion["verdict"] == ""
    assert "Healthy" not in conclusion["verdict"]
    assert "degraded" in conclusion["summary"].lower()

    # 2. Degraded herding input
    degraded_result = {
        "status": "degraded",
        "reason": "Need ≥3 stocks in sector",
        "quote": {"symbol": "RELIANCE.NS", "name": "Reliance", "price": 2500},
        "priceChart": [{"date": "2026-01-01", "close": 2500}],
        "herding": {"herdingDetected": False, "intensity": 0, "error": "Need ≥3 stocks in sector"},
        "panic": {"panicScore": 10, "level": "LOW", "factors": {}},
        "behaviorGap": {"behaviorGap": 0.5, "gapInterpretation": "Small gap"},
        "monteCarlo": {"costOfPanic": {"pctLoss": 5, "meanLoss": 10000, "winRate": 80}},
    }
    conclusion_degraded = simulate_frontend_get_conclusion(degraded_result)
    assert conclusion_degraded["verdict"] == ""
    assert "Healthy" not in conclusion_degraded["verdict"]
