"""Internal REST API."""
from __future__ import annotations

from fastapi import APIRouter, Request, HTTPException

from ..modules.policy import allow_flow
from ..modules.installer import install_flow

router = APIRouter()


@router.post("/flows")
async def create_flow(req: Request) -> dict[str, str]:
    data = await req.json()
    if not allow_flow(data):
        raise HTTPException(status_code=403, detail="blocked")
    await install_flow("http://ryu", data)
    return {"status": "installed"}
