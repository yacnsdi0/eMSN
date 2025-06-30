
"""Packet‑In forwarder app with retry/back‑off and optional TLS."""
import asyncio, json, ssl, os, logging
from aiohttp import ClientSession, ClientConnectorError
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from sanitizer import sanitize, PacketInEvent

FM_URL = os.getenv("FM_URL", "https://flow-manager:8443/flowmanager/packetin")
SS_URL = os.getenv("SS_URL", "https://simpleswitch:8443/packetin")
MAX_RETRY = int(os.getenv("MAX_RETRY", "3"))
TLS_CERT = os.getenv("TLS_CERT")  # path to client cert
TLS_KEY = os.getenv("TLS_KEY")

ssl_ctx = None
if TLS_CERT and TLS_KEY:
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.load_cert_chain(TLS_CERT, TLS_KEY)

log = logging.getLogger("pipu")

class PacketInForwarder(app_manager.RyuApp):
    async def _post(self, url: str, payload: PacketInEvent):
        backoff = 1
        async with ClientSession(conn_timeout=3, timeout=3) as sess:
            for attempt in range(1, MAX_RETRY + 1):
                try:
                    async with sess.post(url, json=json.loads(payload.json()), ssl=ssl_ctx) as resp:
                        if resp.status < 400:
                            return
                        log.warning("POST %s returned %s", url, resp.status)
                except ClientConnectorError as exc:
                    log.warning("Conn error %s attempt %d", exc, attempt)
                await asyncio.sleep(backoff)
                backoff *= 2
            log.error("Failed to POST %s after %d attempts", url, MAX_RETRY)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _handle_pkt_in(self, ev):
        try:
            model = sanitize(ev.msg)
        except Exception as exc:
            log.debug("sanitize failed: %s", exc)
            return
        asyncio.ensure_future(self._post(FM_URL, model))
        asyncio.ensure_future(self._post(SS_URL, model))
