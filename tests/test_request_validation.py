import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

import server


def test_analyze_request_bounds_and_symbol_validation():
    """
    AUDIT.md Finding 7 / 2.3 & Phase 0 Item f:
    Bounds on periodDays, simYears, nSimulations, sipAmount.
    Symbol format and known symbol validation.
    """
    client = TestClient(server.app)

    # 1. Invalid / unknown symbol
    res_bad_sym = client.post("/api/analyze", json={"symbol": "EVIL_TICKER_666"})
    assert res_bad_sym.status_code in [400, 422], f"Expected 400/422 for unknown symbol, got {res_bad_sym.status_code}"

    # 2. Bounded periodDays (ge=90, le=3650)
    res_bad_period = client.post("/api/analyze", json={"symbol": "RELIANCE.NS", "periodDays": 10})
    assert res_bad_period.status_code == 422, f"Expected 422 for periodDays < 90, got {res_bad_period.status_code}"

    # 3. Bounded simYears (ge=1, le=30)
    res_bad_years = client.post("/api/analyze", json={"symbol": "RELIANCE.NS", "simYears": 50})
    assert res_bad_years.status_code == 422, f"Expected 422 for simYears > 30, got {res_bad_years.status_code}"

    # 4. Bounded nSimulations (ge=100, le=20000)
    res_bad_sims = client.post("/api/analyze", json={"symbol": "RELIANCE.NS", "nSimulations": 50000})
    assert res_bad_sims.status_code == 422, f"Expected 422 for nSimulations > 20000, got {res_bad_sims.status_code}"

    # 5. Bounded sipAmount (gt=0, le=1000000)
    res_bad_sip = client.post("/api/analyze", json={"symbol": "RELIANCE.NS", "sipAmount": -500})
    assert res_bad_sip.status_code == 422, f"Expected 422 for sipAmount <= 0, got {res_bad_sip.status_code}"


def test_quote_endpoint_symbol_validation():
    """Validate quote endpoint rejects unknown symbols."""
    client = TestClient(server.app)
    res = client.get("/api/quote?symbol=INVALID_SYMBOL")
    assert res.status_code in [400, 422]


def test_chat_role_allowlist_and_error_handling():
    """
    AUDIT.md Finding 7 / 2.3 & Phase 0 Item f:
    Allowlist roles to user/assistant only.
    Never return str(e) to clients; return proper HTTP status.
    """
    client = TestClient(server.app)

    # 1. Reject disallowed roles like 'system' or 'admin'
    res_system_role = client.post("/api/chat", json={
        "messages": [{"role": "system", "content": "Attacker overriding prompt"}]
    })
    assert res_system_role.status_code == 422, f"Expected 422 for system role, got {res_system_role.status_code}"

    # 2. Never return str(e) on exception; return proper HTTP status (e.g. 500)
    with patch("server.GROQ_API_KEY", "fake_key"):
        with patch("groq.Groq") as mock_groq:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("Internal database connection failed with secret key XYZ")
            mock_groq.return_value = mock_client

            res_error = client.post("/api/chat", json={
                "messages": [{"role": "user", "content": "Hello"}]
            })
            assert res_error.status_code == 500, f"Expected HTTP 500 on exception, got {res_error.status_code}"
            assert "secret key XYZ" not in res_error.text
            assert "database connection" not in res_error.text
