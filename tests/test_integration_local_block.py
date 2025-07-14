import os
import sys
import asyncio

import httpx
import pytest

base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(base, "flow-manager"))  # noqa: E402
sys.path.insert(0, base)  # noqa: E402
sys.modules.pop("flow_manager", None)

from etcd3mock import Etcd3Client  # noqa: E402
from flow_manager.app import create_app  # noqa: E402
from flow_manager.config import Settings  # noqa: E402
from flow_manager.etcd.client import SecureETCDClient  # noqa: E402
from flow_manager.modules import installer  # noqa: E402
import flow_manager.security.jwt_middleware as jwt_middleware  # noqa: E402


def test_local_block(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _run() -> None:
        settings = Settings()
        settings.ryu_rest = "http://ryu"
        etcd = SecureETCDClient(Etcd3Client(), settings)
        etcd.put_host("10.0.0.1", {"mac": "aa:aa:aa:aa:aa:aa", "dpid": "s1", "port": 1})
        etcd.put_host("10.0.0.8", {"mac": "bb:bb:bb:bb:bb:bb", "dpid": "s1", "port": 8})

        monkeypatch.setattr(
            jwt_middleware.PyJWKClient,
            "get_signing_key_from_jwt",
            lambda *a, **k: type("K", (), {"key": "secret"})(),
        )
        monkeypatch.setattr(
            jwt_middleware,
            "jwt",
            type("J", (), {"decode": lambda *a, **k: {"scope": "flows:write"}})(),
        )

        requests: list[httpx.Request] = []

        async def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json={})

        installer._CLIENT = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        installer.settings.ryu_rest = "http://ryu"

        app = create_app()
        app.state.etcd = etcd

        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            token = "a.b.c"
            body = {
                "src_ip": "10.0.0.1",
                "dst_ip": "10.0.0.8",
                "action": "block",
                "switch": "s1",
                "in_port": 1,
            }
            resp = await client.post(
                "/api/v1/flows",
                json=body,
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 202
            flow_id = resp.json()["flow_id"]

        assert requests
        data = requests[0].json()
        assert data.get("actions") == []
        key = f"/domain/{settings.domain_id}/flows/{flow_id}"
        assert key in etcd.client.store

    asyncio.run(_run())
