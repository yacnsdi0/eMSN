"""Topology ingestion module."""

from __future__ import annotations

from datetime import datetime, timezone
import ipaddress
from fastapi import FastAPI

from ..etcd.client import SecureETCDClient


async def process_topology(app: FastAPI, payload: dict) -> None:
    """Validate and store topology information into ETCD."""

    if "hosts" not in payload or "switches" not in payload:
        raise ValueError("invalid topology payload")

    etcd: SecureETCDClient = app.state.etcd
    now = datetime.now(timezone.utc).isoformat()

    for host in payload["hosts"]:
        ip = str(ipaddress.ip_address(host["ip"]))
        key = f"/hosts/{ip}"
        existing = etcd.get(key)
        data = host | {"last_seen": now}
        if existing is None:
            data["first_seen"] = now
        etcd.put_host(ip, data)

    for switch in payload["switches"]:
        name = switch.get("dpid") or switch.get("id")
        if name is None:
            continue
        key = f"/switches/{name}"
        existing = etcd.get(key)
        data = switch | {"last_seen": now}
        if existing is None:
            data["first_seen"] = now
        etcd.put_switch(name, data)
