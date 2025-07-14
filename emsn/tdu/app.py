"""Topology Discovery Unit (TDU) – skeleton v0.1.

Injects LLDP, ingests LLDP/ARP, computes topology deltas, POSTs to Flow‑Manager.

NOTE: This is a **skeleton**. Parts marked TODO must be completed during the
next coding sprint (e.g., detailed LLDP injection scheduling, graph diff emit
loop).
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any

import httpx
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls

from .arp import parse_arp
from .discovery_state import TopologyState
from .lldp import parse_lldp

CID = os.getenv("CID", "controller-1")
LLDP_INTERVAL = int(os.getenv("LLDP_INTERVAL", "10"))
FM_TOPO_URL = os.getenv(
    "FM_TOPO_URL", "https://flow-manager:8443/flowmanager/topology_update"
)
FM_CERT = os.getenv("TDU_CERT", "/certs/tdu.pem")
FM_KEY = os.getenv("TDU_KEY", "/certs/tdu.key")
FM_CA = os.getenv("FM_CA", "/certs/ca.pem")
FM_JWT = os.getenv("TDU_JWT")

log = logging.getLogger("tdu")


class TopologyDiscoveryApp(app_manager.RyuApp):  # type: ignore[misc]
    _CONTEXTS: dict[str, object] = {}

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.state = TopologyState()
        self.loop_task: asyncio.Task[None] | None = None

    def start(self) -> None:
        super().start()
        self.loop_task = asyncio.ensure_future(self._inject_loop())
        log.info("TDU started, posting to %s", FM_TOPO_URL)

    async def _inject_loop(self) -> None:
        """Periodically craft and inject LLDP per port (TODO real datapath list)."""
        while True:
            # TODO: iterate datapaths, send LLDP using build_lldp()
            await asyncio.sleep(LLDP_INTERVAL)

    async def _post_delta(self, delta: dict[str, Any]) -> None:
        if not delta:
            return
        payload = {
            "cid": CID,
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            **delta,
        }
        headers = {}
        if FM_JWT:
            headers["Authorization"] = f"Bearer {FM_JWT}"
        async with httpx.AsyncClient(
            cert=(FM_CERT, FM_KEY), verify=FM_CA, timeout=3.0
        ) as client:
            try:
                resp = await client.post(FM_TOPO_URL, json=payload, headers=headers)
                log.debug("POST %s -> %s", FM_TOPO_URL, resp.status_code)
            except Exception as exc:
                log.warning("POST failed: %s", exc)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)  # type: ignore[misc]
    def _on_packet_in(self, ev: Any) -> None:
        msg = ev.msg
        # Attempt LLDP parse
        lldp_parsed = parse_lldp(msg.data)
        if lldp_parsed:
            self.state.ingest_link(*lldp_parsed)
        # Attempt ARP host parse
        host = parse_arp(msg.data)
        if host:
            self.state.ingest_host(*host)
        delta = self.state.delta()
        asyncio.ensure_future(self._post_delta(delta))
