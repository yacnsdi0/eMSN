"""Event ingestion endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from ..modules import policy, installer, topology

router = APIRouter()


class HostModel(BaseModel):
    ip: str
    mac: str
    dpid: str | None = None
    port: int | None = None


class SwitchModel(BaseModel):
    dpid: str
    name: str | None = None


class TopologyEvent(BaseModel):
    hosts: list[HostModel]
    switches: list[SwitchModel]


class ResultResponse(BaseModel):
    result: str


class DecisionResponse(BaseModel):
    decision: str


@router.post(
    "/flowmanager/topology_update",
    status_code=202,
    response_model=ResultResponse,
)
async def topology_update(event: TopologyEvent, request: Request) -> ResultResponse:
    await topology.process_topology(request.app, event.dict())
    return ResultResponse(result="queued")


class PacketInEvent(BaseModel):
    src_ip: str
    dst_ip: str
    in_port: int
    dpid: str
    proto: str | None = None
    vlan: int | None = None


@router.post(
    "/flowmanager/packetin",
    status_code=202,
    response_model=DecisionResponse,
)
async def packet_in(event: PacketInEvent, request: Request) -> DecisionResponse:
    etcd = request.app.state.etcd
    decision = policy.decide(
        etcd,
        src_ip=event.src_ip,
        dst_ip=event.dst_ip,
        proto=event.proto,
        vlan=event.vlan,
    )
    match = {"ipv4_src": event.src_ip, "ipv4_dst": event.dst_ip}
    if event.vlan is not None:
        match["vlan_vid"] = event.vlan
    if event.proto is not None:
        match["ip_proto"] = event.proto
    if decision == "allow":
        flow_id = await installer.add_forward_rule(event.dpid, event.in_port, 1, match)
    else:
        flow_id = await installer.add_drop_rule(event.dpid, match)
    etcd.put_flow(flow_id, {"switch": event.dpid, "decision": decision})
    return DecisionResponse(decision=decision)
