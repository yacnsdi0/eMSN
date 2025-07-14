import asyncio
import httpx
import pytest

from simpleswitch.app import create_app

pytestmark = pytest.mark.unit


def test_stats(monkeypatch):
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json_data={"stats": []})

    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda *a, **k: original(transport=httpx.MockTransport(handler)),
    )

    app = create_app()

    async def _run() -> None:
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            resp = await client.get("/stats/flow/1")
            assert resp.status_code == 200

    asyncio.run(_run())

    assert requests
    assert requests[0].url.endswith("/stats/flow/1")
