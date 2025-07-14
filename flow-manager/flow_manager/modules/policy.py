"""Simple allow/block policy engine."""

from __future__ import annotations

import json
import ipaddress
from typing import Any


def _load_policies(etcd: Any) -> list[dict]:
    """Load policies from ETCD in insertion order."""

    prefix = f"{etcd.prefix}/policies/"
    policies: list[dict] = []
    for key, value in etcd.client.store.items():
        if key.startswith(prefix):
            policies.append(json.loads(value))
    return policies


def decide(
    etcd: Any,
    *,
    src_ip: str,
    dst_ip: str,
    proto: str | None,
    vlan: int | None,
) -> str:
    """Return "allow" or "block" for the given flow."""

    policies = _load_policies(etcd)
    src = ipaddress.ip_address(src_ip)
    dst = ipaddress.ip_address(dst_ip)

    for policy in policies:
        if "src_cidr" in policy and src not in ipaddress.ip_network(policy["src_cidr"]):
            continue
        if "dst_cidr" in policy and dst not in ipaddress.ip_network(policy["dst_cidr"]):
            continue
        if "proto" in policy and proto != policy["proto"]:
            continue
        if "vlan" in policy and vlan != policy["vlan"]:
            continue
        return policy.get("action", "allow")

    return "block"
