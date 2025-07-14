"""FastAPI application factory for Flow Manager."""

from __future__ import annotations

from fastapi import FastAPI

from .config import Settings
from .rate_limit import RateLimiterMiddleware
from .security.jwt_middleware import JWTMiddleware
from .api import internal, events, peer, debug


def create_app() -> FastAPI:
    """Create and configure the FastAPI app."""
    settings = Settings()
    app = FastAPI(title="Flow Manager")
    app.state.settings = settings
    app.add_middleware(JWTMiddleware)
    app.add_middleware(RateLimiterMiddleware)

    app.include_router(events.router, tags=["events"])
    app.include_router(internal.router, prefix="/api/v1", tags=["control"])
    app.include_router(peer.router, tags=["peer"])
    app.include_router(debug.router, tags=["debug"])

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
