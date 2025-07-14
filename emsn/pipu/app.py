"""Packet‑In forwarder app with retry/back‑off and optional TLS."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import ssl
import time

from aiohttp import ClientConnectorError, ClientSession
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from sanitizer import PacketInEvent, sanitize

FM_URL = os.getenv("FM_URL", "https://flow-manager:8443/flowmanager/packetin")
SS_URL = os.getenv("SS_URL", "https://simpleswitch:8443/packetin")
MAX_RETRY = int(os.getenv("MAX_RETRY", "3"))
TLS_CERT = os.getenv("TLS_CERT")  # path to client cert
TLS_KEY = os.getenv("TLS_KEY")
CA_BUNDLE = os.getenv("CA_BUNDLE")
NRF_TOKEN_URL = os.getenv("NRF_TOKEN_URL", "https://nrf:9443/token")

ssl_ctx = None
if TLS_CERT and TLS_KEY:
    ssl_ctx = ssl.create_default_context(cafile=CA_BUNDLE)
    ssl_ctx.load_cert_chain(TLS_CERT, TLS_KEY)

log = logging.getLogger("pipu")


class PacketInForwarder(app_manager.RyuApp):  # type: ignore[misc]
    _CONTEXTS: dict[str, object] = {}

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.token: str = ""
        self.token_expiry: float = 0.0
        self.token_task: asyncio.Task[None] | None = None

    def start(self) -> None:
        super().start()
        self.token_task = asyncio.ensure_future(self._token_refresh_loop())
        log.info("PIPU started, FM: %s SS: %s", FM_URL, SS_URL)

    async def _post(self, url: str, payload: PacketInEvent) -> None:
        backoff = 1
        async with ClientSession(conn_timeout=3, timeout=3) as sess:
            for attempt in range(1, MAX_RETRY + 1):
                try:
                    headers = {}
                    if self.token:
                        headers["Authorization"] = f"Bearer {self.token}"
                    async with sess.post(
                        url,
                        json=json.loads(payload.json()),
                        ssl=ssl_ctx,
                        headers=headers,
                    ) as resp:
                        if resp.status < 400:
                            return
                        log.warning("POST %s returned %s", url, resp.status)
                except ClientConnectorError as exc:
                    log.warning("Conn error %s attempt %d", exc, attempt)
                await asyncio.sleep(backoff)
                backoff *= 2
            log.error("Failed to POST %s after %d attempts", url, MAX_RETRY)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)  # type: ignore[misc]
    def _handle_pkt_in(self, ev: object) -> None:
        try:
            model = sanitize(ev.msg)  # type: ignore[attr-defined]
        except Exception as exc:
            log.debug("sanitize failed: %s", exc)
            return
        asyncio.ensure_future(self._post(FM_URL, model))
        asyncio.ensure_future(self._post(SS_URL, model))

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
