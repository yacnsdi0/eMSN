"""Simple per-IP async rate limiter."""

from __future__ import annotations

import asyncio
from typing import Any, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Middleware limiting concurrent requests per client IP."""

    def __init__(self, app: Any, limit_per_host: int = 10) -> None:
        super().__init__(app)
        self.limit_per_host = limit_per_host
        self.semaphores: dict[str, asyncio.Semaphore] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        ip = request.client.host
        sem = self.semaphores.setdefault(ip, asyncio.Semaphore(self.limit_per_host))
        if sem.locked() and sem._value == 0:  # not exported; acceptable for toy
            raise HTTPException(
                status_code=429, detail="rate limit", headers={"Retry-After": "2"}
            )
        async with sem:
            return await call_next(request)
