"""Internal REST API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ..grpc import FlowRequest
from ..modules import installer, peer, policy

router = APIRouter()


class FlowRequestBody(BaseModel):
    src_ip: str = Field(..., alias="src_ip")
    dst_ip: str = Field(..., alias="dst_ip")
    proto: str | None = None
    src_port: int | None = None
    dst_port: int | None = None
    vlan: int | None = None
    action: str
    switch: str
    in_port: int


class FlowCreateResponse(BaseModel):
    flow_id: str


class ResultResponse(BaseModel):
    result: str


@router.post("/flows", status_code=202, response_model=FlowCreateResponse)
async def create_flow(body: FlowRequestBody, request: Request) -> FlowCreateResponse:
    etcd = request.app.state.etcd
    decision = policy.decide(
        etcd,
        src_ip=body.src_ip,
        dst_ip=body.dst_ip,
        proto=body.proto,
        vlan=body.vlan,
    )
    if decision != body.action:
        raise HTTPException(status_code=409, detail="policy mismatch")
    match = {"ipv4_src": body.src_ip, "ipv4_dst": body.dst_ip}
    if body.vlan is not None:
        match["vlan_vid"] = body.vlan
    if body.proto is not None:
        match["ip_proto"] = body.proto
    if body.action == "allow":
        flow_id = await installer.add_forward_rule(body.switch, body.in_port, 1, match)
    else:
        flow_id = await installer.add_drop_rule(body.switch, match)
    record = body.model_dump() | {"remote": False, "switch": body.switch}
    dest_host = etcd.get(f"/hosts/{body.dst_ip}")
    if (
        dest_host
        and dest_host.get("domain")
        and dest_host["domain"] != request.app.state.settings.domain_id
    ):
        domain_id = int(dest_host["domain"])
        await peer.install_flow_remote(
            domain_id, FlowRequest(id=flow_id, switch=body.switch)
        )
        record["remote"] = True
        record["remote_domain"] = domain_id
    etcd.put_flow(flow_id, record)
    return FlowCreateResponse(flow_id=flow_id)


@router.delete("/flows/{flow_id}", status_code=202, response_model=ResultResponse)
async def delete_flow(flow_id: str, request: Request) -> ResultResponse:
    etcd = request.app.state.etcd
    record = etcd.get(f"/flows/{flow_id}") or {}
    await installer.delete_rule(flow_id)
    if record.get("remote_domain"):
        await peer.delete_flow_remote(
            int(record["remote_domain"]),
            FlowRequest(id=flow_id, switch=str(record.get("switch", ""))),
        )
    etcd.delete(f"/flows/{flow_id}")
    return ResultResponse(result="deleted")
