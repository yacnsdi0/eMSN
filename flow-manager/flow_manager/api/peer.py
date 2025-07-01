"""Peer gateway API (placeholder)."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("/flows")
async def peer_flow() -> dict[str, str]:
    return {"status": "peer"}
