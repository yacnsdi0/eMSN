from __future__ import annotations

import os

import httpx
from fastapi import FastAPI

RYU_REST = os.getenv("RYU_REST", "http://ryu:8080")


def create_app() -> FastAPI:
    app = FastAPI(title="SimpleSwitch")

    async def _fetch(path: str) -> dict[str, object]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{RYU_REST}{path}")
            return resp.json()

    @app.get("/stats/flow/{dpid}")
    async def flow_stats(dpid: str) -> dict[str, object]:
        return await _fetch(f"/stats/flow/{dpid}")

    @app.get("/stats/port/{dpid}")
    async def port_stats(dpid: str) -> dict[str, object]:
        return await _fetch(f"/stats/port/{dpid}")

    @app.get("/stats/table/{dpid}")
    async def table_stats(dpid: str) -> dict[str, object]:
        return await _fetch(f"/stats/table/{dpid}")

    return app


app = create_app()
