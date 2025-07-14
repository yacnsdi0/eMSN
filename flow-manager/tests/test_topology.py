import os
import sys

base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base)  # noqa: E402
sys.path.insert(0, os.path.join(base, "flow-manager"))  # noqa: E402

import asyncio  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from flow_manager.modules.topology import process_topology  # noqa: E402


class DummyETCD:
    def __init__(self) -> None:
        self.store = {}

    def get(self, key: str):
        return self.store.get(key)

    def put_host(self, name: str, value: dict) -> None:
        self.store[f"/hosts/{name}"] = value

    def put_switch(self, name: str, value: dict) -> None:
        self.store[f"/switches/{name}"] = value


def test_process_topology():
    app = FastAPI()
    app.state.etcd = DummyETCD()
    payload = {"hosts": [{"ip": "10.0.0.1", "mac": "aa"}], "switches": [{"dpid": "1"}]}
    asyncio.run(process_topology(app, payload))
    host = app.state.etcd.store["/hosts/10.0.0.1"]
    sw = app.state.etcd.store["/switches/1"]
    assert host["mac"] == "aa"
    assert "first_seen" in host and "last_seen" in host
    assert sw["dpid"] == "1"
    assert "first_seen" in sw
