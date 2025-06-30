
"""discovery_state.py – in-memory topology graph & diff engine."""
from typing import Dict, Any

class TopologyState:
    def __init__(self):
        self.switches = {}
        self.links = set()
        self.hosts = {}
        self._prev_snapshot = {}

    # Ingest methods ---------------------------------------------------------
    def ingest_link(self, src_dpid, src_port, dst_dpid, dst_port):
        self.links.add((src_dpid, src_port, dst_dpid, dst_port))

    def ingest_host(self, ip, mac):
        self.hosts[ip] = mac

    # Diff -------------------------------------------------------------------
    def delta(self) -> Dict[str, Any]:
        snapshot = {"switches": self.switches.copy(),
                    "links": sorted(self.links),
                    "hosts": self.hosts.copy()}
        delta = {}
        if snapshot != self._prev_snapshot:
            delta = snapshot
            self._prev_snapshot = snapshot
        return delta
