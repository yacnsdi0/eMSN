"""Peer gateway API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..grpc import FlowAck, FlowRequest
from ..modules import peer

router = APIRouter()


class FlowRequestModel(BaseModel):
    id: str
    switch: str
    target_domain: int | None = None


@router.post("/peer/v1/flows", status_code=202, response_model=FlowAck)
async def peer_flow(
    body: FlowRequestModel, target_domain: int | None = Query(None)
) -> FlowAck:
    domain = target_domain if target_domain is not None else body.target_domain
    if domain is None:
        raise HTTPException(status_code=400, detail="target domain required")
    req = FlowRequest(id=body.id, switch=body.switch)
    return await peer.install_flow_remote(domain, req)
