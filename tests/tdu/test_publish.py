import httpx
import pytest

ryu = pytest.importorskip("ryu")
from emsn.tdu.app import TopologyDiscoveryApp, FM_TOPO_URL, FM_JWT  # noqa: E402

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_publish(monkeypatch):
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={})

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda *a, **k: httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    app = TopologyDiscoveryApp()
    app.state.ingest_host("10.0.0.1", "aa")
    delta = app.state.delta()
    await app._post_delta(delta)  # type: ignore[attr-defined]

    assert requests
    req = requests[0]
    assert req.url == httpx.URL(FM_TOPO_URL)
    assert req.headers.get("Authorization") == f"Bearer {FM_JWT}"
    body = req.json()
    assert "hosts" in body
    assert "switches" in body
