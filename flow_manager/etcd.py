from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SecureETCDClient:
    """Very small stub representing a secure etcd client."""

    domain_id: str
    ca: str
    cert: str
    key: str
    jwt: str
    host: str
    port: int

    # Real implementation would initialise a connection here
