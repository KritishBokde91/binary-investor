import pytest
from fastapi.testclient import TestClient

import server


def test_cors_rejects_unauthorized_origins_and_disables_credentials():
    """
    AUDIT.md Finding 8 / 2.3 & Phase 0 Item g:
    CORS: replace allow_origins=['*'] + credentials with an explicit origin list
    from an env var, credentials off.
    """
    client = TestClient(server.app)

    # 1. Unauthorized origin: https://evil.example
    headers_evil = {
        "Origin": "https://evil.example",
        "Access-Control-Request-Method": "GET",
    }
    res_evil = client.options("/api/health", headers=headers_evil)
    # Must NOT reflect evil origin
    assert res_evil.headers.get("access-control-allow-origin") != "https://evil.example"
    # Credentials MUST be off
    assert res_evil.headers.get("access-control-allow-credentials") != "true"

    # 2. Authorized origin: http://localhost:3000
    headers_good = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
    }
    res_good = client.options("/api/health", headers=headers_good)
    assert res_good.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert res_good.headers.get("access-control-allow-credentials") != "true"
