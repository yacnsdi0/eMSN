from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import get_settings
from .etcd import SecureETCDClient
from .rate_limit import ClientLimiter, rate_limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = get_settings()
    app.state.limiter = ClientLimiter(cfg.max_concurrent)
    app.state.etcd = SecureETCDClient(
        domain_id=cfg.domain_id,
        ca=cfg.ca,
        cert=cfg.cert,
        key=cfg.key,
        jwt="internal-system-token",
        host=cfg.etcd_host,
        port=cfg.etcd_port,
    )
    yield


app = FastAPI(
    title="Flow Manager",
    version="0.1.0",
    lifespan=lifespan,
)

app.middleware("http")(rate_limiter)


@app.get("/health")
async def health():
    return {"status": "ok"}
