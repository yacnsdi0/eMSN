import os
import sys

base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base)  # noqa: E402
sys.path.insert(0, os.path.join(base, "flow-manager"))  # noqa: E402

import asyncio  # noqa: E402
import httpx  # noqa: E402
from flow_manager.modules import installer  # noqa: E402


def test_add_drop_rule_request():
    requests = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append((request.method, request.url, request.json()))
        return httpx.Response(200, json_data={})

    installer._CLIENT = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    installer.settings.ryu_rest = "http://ryu"

    flow_id = asyncio.run(installer.add_drop_rule("1", {"eth_type": 2048}))
    assert requests[0][0] == "POST"
    assert requests[0][1] == "http://ryu/stats/flowentry/add"
    assert requests[0][2]["dpid"] == "1"
    assert flow_id
