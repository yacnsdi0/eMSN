"""discovery_state.py – in-memory topology graph & diff engine."""

from typing import Any, Dict


class TopologyState:
    def __init__(self) -> None:
        self.switches: dict[int, dict[str, Any]] = {}
        self.links: set[tuple[int, int, int, int]] = set()
        self.hosts: dict[str, str] = {}
        self._prev_snapshot: dict[str, Any] = {}

    # Ingest methods ---------------------------------------------------------
    def ingest_link(
        self, src_dpid: int, src_port: int, dst_dpid: int, dst_port: int
    ) -> None:
        self.links.add((src_dpid, src_port, dst_dpid, dst_port))

    def ingest_host(self, ip: str, mac: str) -> None:
        self.hosts[ip] = mac

    # Diff -------------------------------------------------------------------
    def delta(self) -> Dict[str, Any]:
        snapshot = {
            "switches": self.switches.copy(),
            "links": sorted(self.links),
            "hosts": self.hosts.copy(),
        }
        delta = {}
        if snapshot != self._prev_snapshot:
            delta = snapshot
            self._prev_snapshot = snapshot
        return delta
