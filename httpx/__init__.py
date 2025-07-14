from __future__ import annotations

from typing import Any

from . import _client as _client  # noqa: F401
from . import _types as _types  # noqa: F401


class BaseTransport:
    pass


class Request:
    def __init__(self, method: str, url: str, json: Any | None = None):
        self.method = method
        self.url = url
        self._json = json

    def json(self) -> Any:
        return self._json


class Response:
    def __init__(self, status_code: int = 200, json_data: Any | None = None) -> None:
        self.status_code = status_code
        self._json = json_data or {}

    def json(self) -> Any:
        return self._json


class Client:
    def __init__(
        self, app: Any | None = None, base_url: str = "http://testserver"
    ) -> None:
        self.app = app
        self.base_url = base_url

    def request(self, method: str, url: str, **kwargs: Any) -> Response:
        return Response()


class AsyncClient:
    def __init__(self, *, timeout: float | int | None = None, transport: Any | None = None, base_url: str = "") -> None:
        self.timeout = timeout
        self.transport = transport
        self.base_url = base_url.rstrip("/")

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: Any
    ) -> None:
        pass

    async def request(
        self, method: str, url: str, *, json: Any | None = None, timeout: int | float | None = None
    ) -> Response:
        if url.startswith("/") and self.base_url:
            url = f"{self.base_url}{url}"
        req = Request(method, url, json)
        if self.transport and hasattr(self.transport, "handler"):
            return await self.transport.handler(req)
        return Response()

    async def get(self, url: str, timeout: int | float | None = None) -> Response:
        return await self.request("GET", url, timeout=timeout)

    async def post(
        self, url: str, *, json: Any | None = None, timeout: int | float | None = None
    ) -> Response:
        return await self.request("POST", url, json=json, timeout=timeout)


class MockTransport:
    def __init__(self, handler: Any) -> None:
        self.handler = handler
