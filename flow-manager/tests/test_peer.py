import os
import sys

base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base)  # noqa: E402
sys.path.insert(0, os.path.join(base, "flow-manager"))  # noqa: E402

import asyncio  # noqa: E402
import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from flow_manager.modules.peer import PeerService  # noqa: E402
from flow_manager.grpc import FlowRequest, FlowServiceStub  # noqa: E402
from grpclib.testing import MemoryTransport  # noqa: E402
from grpclib.client import Channel  # noqa: E402
from grpclib.exceptions import GRPCError  # noqa: E402
from grpclib.const import Status  # noqa: E402


def make_token(scope: str) -> str:
    import base64
    import json

    header = base64.urlsafe_b64encode(b"{}").rstrip(b"=").decode()
    payload = (
        base64.urlsafe_b64encode(json.dumps({"scope": scope}).encode())
        .rstrip(b"=")
        .decode()
    )
    return f"{header}.{payload}.sig"


class DummyEtcd:
    def __init__(self) -> None:
        self.data = {}

    def put_flow(self, name: str, value: dict) -> None:
        self.data[f"/flows/{name}"] = value

    def delete(self, key: str) -> None:
        self.data.pop(key, None)


def test_grpc_auth():
    app = FastAPI()
    app.state.etcd = DummyEtcd()
    service = PeerService(app)
    transport = MemoryTransport(service)
    channel = Channel(transport=transport)
    stub = FlowServiceStub(channel)
    good_token = make_token("flows:write")
    bad_token = make_token("flows:read")

    req = FlowRequest(id="1", switch="s1")
    # good token
    resp = asyncio.run(
        stub.InstallFlow(req, metadata={"authorization": f"Bearer {good_token}"})
    )
    assert resp.status == "accepted"

    # bad scope
    with pytest.raises(GRPCError) as exc:
        asyncio.run(
            stub.InstallFlow(req, metadata={"authorization": f"Bearer {bad_token}"})
        )
    assert exc.value.status is Status.UNAUTHENTICATED
