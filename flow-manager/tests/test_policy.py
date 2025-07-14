import os
import sys

base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base)  # noqa: E402
sys.path.insert(0, os.path.join(base, "flow-manager"))  # noqa: E402

import json  # noqa: E402
from flow_manager.modules.policy import decide  # noqa: E402


class DummyClient:
    def __init__(self) -> None:
        self.prefix = "/domain/42"
        self.client = type("C", (), {"store": {}})()

    def put_policy(self, name: str, value: dict) -> None:
        self.client.store[f"{self.prefix}/policies/{name}"] = json.dumps(value)


def make_client() -> DummyClient:
    return DummyClient()


def test_allow_match():
    client = make_client()
    client.put_policy("1", {"src_cidr": "10.0.0.0/24", "action": "allow"})
    result = decide(client, src_ip="10.0.0.5", dst_ip="1.1.1.1", proto=None, vlan=None)
    assert result == "allow"


def test_block_default():
    client = make_client()
    result = decide(client, src_ip="1.1.1.1", dst_ip="2.2.2.2", proto=None, vlan=None)
    assert result == "block"


def test_proto_specific():
    client = make_client()
    client.put_policy("1", {"proto": "tcp", "action": "allow"})
    assert (
        decide(client, src_ip="1.1.1.1", dst_ip="2.2.2.2", proto="tcp", vlan=None)
        == "allow"
    )
    assert (
        decide(client, src_ip="1.1.1.1", dst_ip="2.2.2.2", proto="udp", vlan=None)
        == "block"
    )
