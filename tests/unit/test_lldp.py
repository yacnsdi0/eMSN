import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from emsn.tdu.lldp import build_lldp, parse_lldp


def test_lldp_roundtrip():
    raw = build_lldp(1, 2, 3, 4)
    assert parse_lldp(raw) == (1, 2, 3, 4)
