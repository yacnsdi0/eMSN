
"""Topology Discovery Unit (TDU) – skeleton v0.1
Injects LLDP, ingests LLDP/ARP, computes topology deltas, POSTs to Flow‑Manager.

NOTE: This is a **skeleton**. Parts marked TODO must be completed during the next
coding sprint (e.g., detailed LLDP injection scheduling, graph diff emit loop).
"""
import asyncio, json, os, logging
from datetime import datetime, timezone

from aiohttp import ClientSession
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls

from .lldp import build_lldp, parse_lldp
from .arp import parse_arp
from .discovery_state import TopologyState

CID = os.getenv("CID", "controller-1")
FM_URL = os.getenv("FM_URL", "http://flow-manager:8080/flowmanager/topology_update")
LLDP_INTERVAL = int(os.getenv("LLDP_INTERVAL", "10"))

log = logging.getLogger("tdu")

class TopologyDiscoveryApp(app_manager.RyuApp):
    _CONTEXTS = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = TopologyState()
        self.loop_task = None

    def start(self):
        super().start()
        self.loop_task = asyncio.ensure_future(self._inject_loop())
        log.info("TDU started, posting to %s", FM_URL)

    async def _inject_loop(self):
        """Periodically craft and inject LLDP per port (TODO real datapath list)."""
        while True:
            # TODO: iterate datapaths, send LLDP using build_lldp()
            await asyncio.sleep(LLDP_INTERVAL)

    async def _post_delta(self, delta: dict):
        if not delta:  # nothing changed
            return
        payload = {"cid": CID, "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **delta}
        async with ClientSession() as sess:
            try:
                async with sess.post(FM_URL, json=payload) as resp:
                    log.debug("POST %s -> %s", FM_URL, resp.status)
            except Exception as exc:
                log.warning("POST failed: %s", exc)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _on_packet_in(self, ev):
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
