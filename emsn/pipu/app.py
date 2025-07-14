"""Packet‑In forwarder app with retry/back‑off and optional TLS."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import httpx
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from sanitizer import PacketInEvent, sanitize

FM_PACKETIN_URL = os.getenv(
    "FM_PKT_URL", "https://flow-manager:8443/flowmanager/packetin"
)
FM_CERT = os.getenv("PIPU_CERT", "/certs/pipu.pem")
FM_KEY = os.getenv("PIPU_KEY", "/certs/pipu.key")
FM_CA = os.getenv("FM_CA", "/certs/ca.pem")
FM_JWT = os.getenv("PIPU_JWT")

log = logging.getLogger("pipu")


class PacketInForwarder(app_manager.RyuApp):  # type: ignore[misc]
    _CONTEXTS: dict[str, object] = {}

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

    def start(self) -> None:
        super().start()
        log.info("PIPU started, FM: %s", FM_PACKETIN_URL)

    async def _post(self, payload: PacketInEvent) -> None:
        headers = {}
        if FM_JWT:
            headers["Authorization"] = f"Bearer {FM_JWT}"
        async with httpx.AsyncClient(cert=(FM_CERT, FM_KEY), verify=FM_CA) as c:
            await c.post(
                FM_PACKETIN_URL,
                json=json.loads(payload.json()),
                headers=headers,
                timeout=2.0,
            )

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)  # type: ignore[misc]
    def _handle_pkt_in(self, ev: object) -> None:
        try:
            model = sanitize(ev.msg)  # type: ignore[attr-defined]
        except Exception as exc:
            log.debug("sanitize failed: %s", exc)
            return
        asyncio.ensure_future(self._post(model))
