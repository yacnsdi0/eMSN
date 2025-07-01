"""Minimal LLDP encode/decode helpers used in tests.

These functions intentionally implement a very small subset of the LLDP
specification sufficient for the unit tests of this repository.  Real
deployments should rely on a full protocol implementation from a networking
library.
"""

from __future__ import annotations

import struct
from typing import Optional, Tuple

_MAGIC = b"LLDP"


def build_lldp(
    src_dpid: int,
    src_port: int,
    dst_dpid: int = 0,
    dst_port: int = 0,
) -> bytes:
    """Return raw bytes of a toy LLDP frame.

    The frame layout is ``b"LLDP"`` followed by four network‑byte‑order
    integers: ``src_dpid``, ``src_port``, ``dst_dpid`` and ``dst_port``.
    ``dst_dpid`` and ``dst_port`` are optional and default to ``0``.
    """

    return struct.pack(
        "!4sIIII",
        _MAGIC,
        src_dpid,
        src_port,
        dst_dpid,
        dst_port,
    )


def parse_lldp(data: bytes) -> Optional[Tuple[int, int, int, int]]:
    """Decode a toy LLDP frame produced by :func:`build_lldp`.

    Returns ``(src_dpid, src_port, dst_dpid, dst_port)`` if decoding succeeds,
    otherwise ``None``.
    """

    if len(data) < 20:
        return None
    try:
        magic, src_dpid, src_port, dst_dpid, dst_port = struct.unpack(
            "!4sIIII", data[:20]
        )
    except struct.error:
        return None
    if magic != _MAGIC:
        return None
    return src_dpid, src_port, dst_dpid, dst_port
