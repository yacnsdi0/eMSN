from types import SimpleNamespace

import pytest

ryu = pytest.importorskip("ryu")
from ryu.lib.packet import ethernet, ipv4, packet  # noqa: E402

from emsn.pipu.sanitizer import sanitize  # noqa: E402

pytestmark = pytest.mark.unit


class DummyMsg:
    def __init__(self, dpid: int, in_port: int, buffer_id: int, src: str, dst: str):
        self.datapath = SimpleNamespace(id=dpid)
        self.match = {"in_port": in_port}
        pkt = packet.Packet()
        pkt.add_protocol(ethernet.ethernet(src=src, dst=dst, ethertype=0x0800))
        pkt.add_protocol(ipv4.ipv4(src="10.0.0.1", dst="10.0.0.2"))
        pkt.serialize()
        self.data = bytes(pkt.data)
        self.buffer_id = buffer_id


def test_sanitize():
    msg = DummyMsg(1, 2, 3, "aa:bb:cc:dd:ee:ff", "ff:ee:dd:cc:bb:aa")
    event = sanitize(msg)
    assert event.dpid == 1
    assert event.in_port == 2
    assert event.eth_src == "aa:bb:cc:dd:ee:ff"
