"""Flow installer using Ryu REST API."""
from __future__ import annotations

import aiohttp


async def install_flow(url: str, flow_json: dict) -> None:
    async with aiohttp.ClientSession() as session:
        await session.post(f"{url}/stats/flowentry/add", json=flow_json)
