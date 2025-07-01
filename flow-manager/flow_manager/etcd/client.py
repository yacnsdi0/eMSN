"""Secure ETCD client with mTLS and JWT auth."""
from __future__ import annotations

import json
from typing import Any

import etcd3
from jsonschema import validate

from ..config import Settings
from .schema import HOST_SCHEMA, SWITCH_SCHEMA, POLICY_SCHEMA, FLOW_SCHEMA


class SecureETCDClient:
    """Scoped ETCD client using mTLS and JWT metadata."""

    def __init__(self, client: etcd3.Etcd3Client, settings: Settings) -> None:
        self.client = client
        self.prefix = f"/domain/{settings.domain_id}"

    def _put_json(self, key: str, value: dict[str, Any], schema: dict[str, Any]) -> None:
        validate(value, schema)
        self.client.put(f"{self.prefix}{key}", json.dumps(value))

    def put_host(self, name: str, value: dict[str, Any]) -> None:
        self._put_json(f"/hosts/{name}", value, HOST_SCHEMA)

    def put_switch(self, name: str, value: dict[str, Any]) -> None:
        self._put_json(f"/switches/{name}", value, SWITCH_SCHEMA)

    def put_policy(self, name: str, value: dict[str, Any]) -> None:
        self._put_json(f"/policies/{name}", value, POLICY_SCHEMA)

    def put_flow(self, name: str, value: dict[str, Any]) -> None:
        self._put_json(f"/flows/{name}", value, FLOW_SCHEMA)
