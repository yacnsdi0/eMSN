import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from emsn.tdu.discovery_state import TopologyState


def test_state_delta():
    state = TopologyState()
    initial = state.delta()
    assert "links" in initial
    state.ingest_link(1, 1, 2, 2)
    delta = state.delta()
    assert "links" in delta
    assert state.delta() == {}
