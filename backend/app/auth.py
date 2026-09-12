"""Auth boundary: JWT verification, per Interface Contracts section 3.3.

Sits ahead of the API layer -- requests are verified before reaching
route handlers. Chosen (confirmed with Integration Lead) to keep the
backend stateless and simple to scale across instances.

TECH DEBT: the signing secret is a hardcoded placeholder and there is no
token issuance endpoint yet, since Alpha only needs to prove the
verification boundary works. Before Beta this needs a real secret
management story (e.g. AWS Secrets Manager) and a login/issuance flow.
"""
from __future__ import annotations

import os

import jwt
from fastapi import Depends, Header, HTTPException, status

_SECRET = os.environ.get("PAYPARITY_JWT_SECRET", "alpha-placeholder-secret")
_ALGORITHM = "HS256"


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized"},
        ) from exc


def require_auth(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized"},
        )
    token = authorization.removeprefix("Bearer ").strip()
    return decode_token(token)


def require_admin(claims: dict = Depends(require_auth)) -> dict:
    if claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden"},
        )
    return claims
