"""Internal REST API."""

from __future__ import annotations

from fastapi import APIRouter, Request, HTTPException

from ..modules.policy import decide
from ..modules.installer import add_forward_rule

router = APIRouter()


@router.post("/flows")
async def create_flow(req: Request) -> dict[str, str]:
    data = await req.json()
    if (
        decide(
            req.app.state.etcd,
            src_ip=data.get("src_ip", "0.0.0.0"),
            dst_ip=data.get("dst_ip", "0.0.0.0"),
            proto=data.get("proto"),
            vlan=data.get("vlan"),
        )
        == "block"
    ):
        raise HTTPException(status_code=403, detail="blocked")
    await add_forward_rule("dpid", 1, 2, data)
    return {"status": "installed"}
