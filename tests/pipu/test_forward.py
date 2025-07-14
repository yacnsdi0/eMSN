import httpx
import pytest

ryu = pytest.importorskip("ryu")
from emsn.pipu.app import PacketInForwarder, FM_PACKETIN_URL, FM_JWT  # noqa: E402
from emsn.pipu.sanitizer import PacketInEvent  # noqa: E402

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_forward(monkeypatch):
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={})

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda *a, **k: httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    app = PacketInForwarder()
    event = PacketInEvent(
        cid="c",
        ts="2020-01-01T00:00:00Z",
        dpid=1,
        in_port=1,
        buffer_id=0,
        eth_src="aa:bb:cc:dd:ee:ff",
        eth_dst="ff:ee:dd:cc:bb:aa",
        eth_type=2048,
    )
    await app._post(event)  # type: ignore[attr-defined]

    assert requests
    req = requests[0]
    assert req.url == httpx.URL(FM_PACKETIN_URL)
    assert req.headers.get("Authorization") == f"Bearer {FM_JWT}"
    assert req.json()["eth_src"] == "aa:bb:cc:dd:ee:ff"
