from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Dict

from fastapi import Request, Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from typing import Awaitable, Callable


class TimedSemaphore:
    """Wrapper around :class:`asyncio.Semaphore` with timeout support."""

    def __init__(self, value: int) -> None:
        self._sem = asyncio.Semaphore(value)

    async def acquire(self, timeout: float | None = None) -> bool:
        try:
            await asyncio.wait_for(self._sem.acquire(), timeout)
            return True
        except asyncio.TimeoutError:
            return False

    def release(self) -> None:
        self._sem.release()


class ClientLimiter:
    """Concurrency limiter per client IP."""

    def __init__(self, limit: int) -> None:
        self.limit = limit
        self._buckets: Dict[str, TimedSemaphore] = defaultdict(
            lambda: TimedSemaphore(limit)
        )

    def bucket(self, host: str) -> TimedSemaphore:
        return self._buckets[host]


async def rate_limiter(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    limiter: ClientLimiter = request.app.state.limiter
    client_ip = request.client.host if request.client else "unknown"
    sem = limiter.bucket(client_ip)
    if not await sem.acquire(timeout=0):
        return Response(
            "rate limit exceeded",
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            headers={"Retry-After": "2"},
        )
    try:
        return await call_next(request)
    finally:
        sem.release()
