
"""lldp.py – helper to craft & parse LLDP frames (simplified)."""
from typing import Optional, Tuple

def build_lldp(dpid: int, port_no: int) -> bytes:
    """Return raw bytes of an LLDP Ethernet frame (TODO real implementation)."""
    return b""  # placeholder

def parse_lldp(data: bytes) -> Optional[Tuple[int, int, int, int]]:
    """Return (src_dpid, src_port, dst_dpid, dst_port) if data is LLDP."""
    # TODO actual parse implementation
    return None
