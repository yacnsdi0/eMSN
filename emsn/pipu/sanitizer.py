"""Packet‑In sanitisation & schema for PIPU."""

import os
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field, validator
from ryu.lib.packet import ethernet, ipv4, packet, vlan

__all__ = ["PacketInEvent", "sanitize"]


class PacketInEvent(BaseModel):
    cid: str
    ts: str = Field(..., regex=r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
    dpid: int
    in_port: int
    buffer_id: int
    eth_src: str = Field(..., regex=r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$")
    eth_dst: str = Field(..., regex=r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$")
    eth_type: int
    vlan: Optional[int] = None
    ipv4_src: Optional[str] = None
    ipv4_dst: Optional[str] = None


@validator("eth_src", "eth_dst", pre=True)
def lower_mac(cls: type["PacketInEvent"], v: str) -> str:  # noqa
    return v.lower()


def sanitize(ofp_msg: Any) -> PacketInEvent:
    pkt = packet.Packet(ofp_msg.data)
    eth = pkt.get_protocol(ethernet.ethernet)
    vlan_hdr = pkt.get_protocol(vlan.vlan)
    ipv4_hdr = pkt.get_protocol(ipv4.ipv4)

    return PacketInEvent(
        cid=os.getenv("CID", "controller-1"),
        ts=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        dpid=ofp_msg.datapath.id,
        in_port=ofp_msg.match["in_port"],
        buffer_id=ofp_msg.buffer_id,
        eth_src=eth.src,
        eth_dst=eth.dst,
        eth_type=eth.ethertype,
        vlan=vlan_hdr.vid if vlan_hdr else None,
        ipv4_src=ipv4_hdr.src if ipv4_hdr else None,
        ipv4_dst=ipv4_hdr.dst if ipv4_hdr else None,
    )
