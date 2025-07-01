"""Event ingestion endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Request

from ..modules.topology import process_topology
from ..etcd.client import SecureETCDClient

router = APIRouter(prefix="/flowmanager")


@router.post("/topology_update")
async def topology_update(req: Request) -> dict[str, str]:
    data = await req.json()
    client = SecureETCDClient(req.app.state.etcd, req.app.state.settings)
    process_topology(data, client)
    return {"status": "ok"}


@router.post("/packetin")
async def packet_in() -> dict[str, str]:
    return {"status": "queued"}
