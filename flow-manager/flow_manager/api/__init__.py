"""API routers for Flow Manager."""

from __future__ import annotations

from .events import router as events_router
from .internal import router as internal_router
from .peer import router as peer_router
from .debug import router as debug_router

__all__ = [
    "events_router",
    "internal_router",
    "peer_router",
    "debug_router",
]
