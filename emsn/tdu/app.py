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
import ssl
import time
from datetime import datetime, timezone
from typing import Any

from aiohttp import ClientSession
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls

from .arp import parse_arp
from .discovery_state import TopologyState
from .lldp import parse_lldp

CID = os.getenv("CID", "controller-1")
FM_URL = os.getenv("FM_URL", "http://flow-manager:8080/flowmanager/topology_update")
LLDP_INTERVAL = int(os.getenv("LLDP_INTERVAL", "10"))
NRF_TOKEN_URL = os.getenv("NRF_TOKEN_URL", "https://nrf:9443/token")
TLS_CERT = os.getenv("TLS_CERT")
TLS_KEY = os.getenv("TLS_KEY")
CA_BUNDLE = os.getenv("CA_BUNDLE")

log = logging.getLogger("tdu")

ssl_ctx = None
if TLS_CERT and TLS_KEY:
    ssl_ctx = ssl.create_default_context(cafile=CA_BUNDLE)
    ssl_ctx.load_cert_chain(TLS_CERT, TLS_KEY)


class TopologyDiscoveryApp(app_manager.RyuApp):  # type: ignore[misc]
    _CONTEXTS: dict[str, object] = {}

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.state = TopologyState()
        self.loop_task: asyncio.Task[None] | None = None
        self.token: str = ""
        self.token_expiry: float = 0.0
        self.token_task: asyncio.Task[None] | None = None

    def start(self) -> None:
        super().start()
        self.loop_task = asyncio.ensure_future(self._inject_loop())
        self.token_task = asyncio.ensure_future(self._token_refresh_loop())
        log.info("TDU started, posting to %s", FM_URL)

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
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        async with ClientSession() as sess:
            try:
                async with sess.post(
                    FM_URL,
                    json=payload,
                    ssl=ssl_ctx,
                    headers=headers,
                ) as resp:
                    log.debug("POST %s -> %s", FM_URL, resp.status)
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

    async def _fetch_token(self) -> None:
        async with ClientSession() as sess:
            try:
                async with sess.post(NRF_TOKEN_URL, ssl=ssl_ctx) as resp:
                    if resp.status >= 400:
                        log.warning("token fetch status %s", resp.status)
                        return
                    data = await resp.json()
                    self.token = data.get("access_token", "")
                    expires_in = data.get("expires_in", 300)
                    self.token_expiry = time.time() + expires_in
                    log.debug("token fetched, expires in %s", expires_in)
            except Exception as exc:
                log.warning("token fetch failed: %s", exc)

    async def _token_refresh_loop(self) -> None:
        while True:
            await self._fetch_token()
            sleep_for = max(self.token_expiry - time.time() - 300, 60)
            await asyncio.sleep(sleep_for)
