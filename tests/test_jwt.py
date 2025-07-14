from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI

pytest.skip("testclient unavailable", allow_module_level=True)

from fastapi.testclient import TestClient  # noqa: E402
from jose import jwt  # noqa: E402
from flow_manager.security.jwt_middleware import JWTMiddleware  # noqa: E402


def _make_token(scope: str, exp_offset: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "tester",
        "scope": scope,
        "iss": "https://issuer",
        "aud": "flow-manager",
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + exp_offset).timestamp()),
    }
    return jwt.encode(payload, "key", algorithm="ES256")


VALID = _make_token("flows:write", timedelta(minutes=5))
WRONG_SCOPE = _make_token("topology:write", timedelta(minutes=5))
EXPIRED = _make_token("flows:write", timedelta(minutes=-5))


def create_test_app() -> TestClient:
    app = FastAPI()
    app.add_middleware(JWTMiddleware, jwks_url="https://example.com/jwks")

    @app.post("/api/v1/flows")
    async def flows(request):  # type: ignore[empty-body]
        return {"claims": getattr(request.state, "jwt_payload", None)}

    return TestClient(app)


def test_jwt_middleware(monkeypatch):
    async def fake_fetch(_: str) -> dict[str, object]:
        return {}

    monkeypatch.setattr("flow_manager.security.jwt_middleware.fetch_jwks", fake_fetch)
    client = create_test_app()

    r = client.post("/api/v1/flows", headers={"Authorization": f"Bearer {VALID}"})
    assert r.status_code in {200, 202}
    assert r.json()["claims"]["scope"] == "flows:write"

    r = client.post(
        "/api/v1/flows",
        headers={"Authorization": f"Bearer {WRONG_SCOPE}"},
    )
    assert r.status_code == 403

    r = client.post(
        "/api/v1/flows",
        headers={"Authorization": f"Bearer {EXPIRED}"},
    )
    assert r.status_code == 401
