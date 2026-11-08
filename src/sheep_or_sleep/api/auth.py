"""API Authentication scaffolding: API Key and JWT token verification."""

from __future__ import annotations

import os
from typing import Optional
from fastapi import Header, HTTPException, status
import jwt

JWT_ALGORITHM = "HS256"


def verify_auth(
    api_key: Optional[str] = None,
    authorization: Optional[str] = None,
    require_auth: bool = False,
    valid_api_key: Optional[str] = None,
    jwt_secret: Optional[str] = None,
) -> str:
    """Validate API key or JWT bearer token. Returns identified client or 'anonymous'."""
    configured_key = valid_api_key or os.getenv("API_KEY")
    secret = jwt_secret or os.getenv("JWT_SECRET", "dev_secret_key_change_in_production")
    should_enforce = require_auth or os.getenv("REQUIRE_AUTH", "false").lower() in ("true", "1")

    # 1. Check API Key
    if api_key and configured_key and api_key == configured_key:
        return f"apikey:{api_key[:6]}..."

    # 2. Check JWT Bearer Token
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1].strip()
        try:
            payload = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
            return str(payload.get("sub", "authenticated_user"))
        except jwt.PyJWTError:
            if should_enforce:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired authentication token",
                )

    # 3. If auth is strictly required and not authenticated
    if should_enforce:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials",
        )

    return "anonymous"


async def get_auth_user(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None),
) -> str:
    """FastAPI dependency to extract and verify caller identity."""
    return verify_auth(api_key=x_api_key, authorization=authorization)
