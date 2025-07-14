"""Secure ETCD client with mTLS and JWT auth and validation."""

from __future__ import annotations

import json
from typing import Any

import etcd3
from jsonschema import ValidationError, validate
from tenacity import RetryError, retry, stop_after_attempt, wait_exponential

from ..config import Settings
from .schema import SCHEMAS


class SecureETCDClient:
    """Scoped ETCD client using mTLS and JWT metadata."""

    def __init__(self, client: etcd3.Etcd3Client, settings: Settings) -> None:
        self.client = client
        self.prefix = f"/domain/{settings.domain_id}"
        self.jwt = getattr(settings, "jwt", "")

    def _check_key(self, key: str) -> str:
        if not key.startswith("/"):
            raise ValueError("key must start with '/'")
        return key if key.startswith(self.prefix) else f"{self.prefix}{key}"

    def _validate(self, key: str, value: dict[str, Any]) -> None:
        try:
            segment = key.split("/")[3]
            schema_key = segment[:-1] if segment.endswith("s") else segment
            validate(value, SCHEMAS[schema_key])
        except ValidationError as exc:  # pragma: no cover - schema mismatch
            raise ValueError(f"ETCD value schema error: {exc.message}") from exc

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.3))
    def _put_raw(self, key: str, value: str) -> None:
        self.client.put(
            key,
            value,
            metadata=(("authorization", f"Bearer {self.jwt}"),),
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.3))
    def _get_raw(self, key: str) -> str | None:
        val, _ = self.client.get(
            key,
            metadata=(("authorization", f"Bearer {self.jwt}"),),
        )
        return val

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.3))
    def _delete_raw(self, key: str) -> None:
        self.client.delete(
            key,
            metadata=(("authorization", f"Bearer {self.jwt}"),),
        )

    def put(self, key: str, value: dict[str, Any]) -> None:
        key = self._check_key(key)
        self._validate(key, value)
        try:
            self._put_raw(key, json.dumps(value))
        except RetryError as exc:  # pragma: no cover - network errors
            raise RuntimeError("ETCD unavailable") from exc

    def get(self, key: str) -> dict[str, Any] | None:
        key = self._check_key(key)
        try:
            raw = self._get_raw(key)
        except RetryError as exc:  # pragma: no cover - network errors
            raise RuntimeError("ETCD unavailable") from exc
        return None if raw is None else json.loads(raw)

    def delete(self, key: str) -> None:
        key = self._check_key(key)
        try:
            self._delete_raw(key)
        except RetryError as exc:  # pragma: no cover - network errors
            raise RuntimeError("ETCD unavailable") from exc

    def put_host(self, name: str, value: dict[str, Any]) -> None:
        self.put(f"/hosts/{name}", value)

    def put_switch(self, name: str, value: dict[str, Any]) -> None:
        self.put(f"/switches/{name}", value)

    def put_policy(self, name: str, value: dict[str, Any]) -> None:
        self.put(f"/policies/{name}", value)

    def put_flow(self, name: str, value: dict[str, Any]) -> None:
        self.put(f"/flows/{name}", value)

    def cas(self, key: str, old_val: dict[str, Any], new_val: dict[str, Any]) -> bool:
        """Atomically replace value only if current == old_val."""
        key = self._check_key(key)
        self._validate(key, new_val)
        return self.client.transaction(
            compare=[self.client.transactions.value(key) == json.dumps(old_val)],
            success=[self.client.transactions.put(key, json.dumps(new_val))],
            failure=[],
        )
