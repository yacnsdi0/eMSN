"""Topology ingestion module."""
from __future__ import annotations

from typing import Any

from ..etcd.client import SecureETCDClient


def process_topology(data: dict[str, Any], client: SecureETCDClient) -> None:
    """Store hosts and switches into ETCD."""
    for name, host in data.get("hosts", {}).items():
        client.put_host(name, host)
    for name, sw in data.get("switches", {}).items():
        client.put_switch(name, sw)
