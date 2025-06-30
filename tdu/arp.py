
"""arp.py – helper to extract hosts from ARP replies."""
from ryu.lib.packet import packet, arp
from typing import Optional, Tuple

def parse_arp(data: bytes) -> Optional[Tuple[str, str]]:
    """Return (src_ip, src_mac) if ARP reply; else None."""
    pkt = packet.Packet(data)
    arp_hdr = pkt.get_protocol(arp.arp)
    if arp_hdr and arp_hdr.opcode == 2:  # ARP reply
        return arp_hdr.src_ip, arp_hdr.src_mac.lower()
    return None
