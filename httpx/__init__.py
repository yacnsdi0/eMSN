from __future__ import annotations

from typing import Any

from . import _client as _client  # noqa: F401
from . import _types as _types  # noqa: F401


class BaseTransport:
    pass


class Request:
    def __init__(self, method: str, url: str):
        self.method = method
        self.url = url


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
    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: Any
    ) -> None:
        pass

    async def get(self, url: str, timeout: int | float | None = None) -> Response:
        return Response()
