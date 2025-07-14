"""Peer communication via gRPC."""

from __future__ import annotations

import base64
import json
from typing import Any

import jwt
from fastapi import FastAPI

from ..grpc import FlowAck, FlowRequest, FlowServiceBase, FlowServiceStub
from ..etcd.client import SecureETCDClient
from . import installer
from grpclib.client import Channel
from grpclib.exceptions import GRPCError
from grpclib.const import Status
from ..security.mtls_utils import load_ssl_context


def _encode_jwt(payload: dict[str, Any]) -> str:
    header = base64.urlsafe_b64encode(b"{}").rstrip(b"=").decode()
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    return f"{header}.{body}.sig"


class PeerService(FlowServiceBase):
    """gRPC service implementing flow operations."""

    def __init__(self, app: FastAPI) -> None:
        self.app = app
        self.etcd: SecureETCDClient = app.state.etcd

    def _check_auth(self, metadata: dict[str, str]) -> None:
        token = metadata.get("authorization", "").split("Bearer ")[-1]
        if not token:
            raise GRPCError(Status.UNAUTHENTICATED)
        payload = jwt.decode(token, None)
        if "flows:write" not in payload.get("scope", "").split():
            raise GRPCError(Status.UNAUTHENTICATED)

    async def InstallFlow(
        self, request: FlowRequest, *, metadata: dict | None = None
    ) -> FlowAck:
        self._check_auth(metadata or {})
        flow_id = await installer.add_drop_rule(request.switch, {})
        self.etcd.put_flow(flow_id, {"switch": request.switch})
        return FlowAck(status="accepted")

    async def DeleteFlow(
        self, request: FlowRequest, *, metadata: dict | None = None
    ) -> FlowAck:
        self._check_auth(metadata or {})
        await installer.delete_rule(request.id)
        self.etcd.delete(f"/flows/{request.id}")
        return FlowAck(status="accepted")


async def install_flow_remote(domain_id: int, request: FlowRequest) -> FlowAck:
    host = f"fm-{domain_id}"
    ssl = load_ssl_context("cert.pem", "key.pem", "ca.pem")
    async with Channel(host, 8443, ssl=ssl) as channel:
        stub = FlowServiceStub(channel)
        token = _encode_jwt({"scope": "flows:write"})
        return await stub.InstallFlow(
            request, metadata={"authorization": f"Bearer {token}"}
        )
