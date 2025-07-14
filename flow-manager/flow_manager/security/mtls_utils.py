"""mTLS certificate loading utilities."""
from __future__ import annotations

import ssl


def load_ssl_context(certfile: str, keyfile: str, cafile: str) -> ssl.SSLContext:
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cafile)
    ctx.load_cert_chain(certfile, keyfile)
    ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx
