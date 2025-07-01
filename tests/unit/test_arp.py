import pytest

ryu = pytest.importorskip("ryu")
from ryu.lib.packet import arp, ethernet, packet  # noqa: E402

from emsn.tdu.arp import parse_arp  # noqa: E402

pytestmark = pytest.mark.unit


def make_arp_reply(ip: str, mac: str) -> bytes:
    pkt = packet.Packet()
    pkt.add_protocol(ethernet.ethernet(src=mac, dst="ff:ff:ff:ff:ff:ff"))
    pkt.add_protocol(
        arp.arp(
            opcode=arp.ARP_REPLY,
            src_ip=ip,
            dst_ip="0.0.0.0",
            src_mac=mac,
            dst_mac="00:00:00:00:00:00",
        )
    )
    pkt.serialize()
    return bytes(pkt.data)


def test_parse_arp_reply():
    data = make_arp_reply("10.0.0.1", "aa:bb:cc:dd:ee:ff")
    assert parse_arp(data) == ("10.0.0.1", "aa:bb:cc:dd:ee:ff")
