"""JSON Schemas for ETCD values."""

from __future__ import annotations

HOST_SCHEMA = {
    "type": "object",
    "properties": {"mac": {"type": "string"}},
    "required": ["mac"],
}

SWITCH_SCHEMA = {
    "type": "object",
    "properties": {"dpid": {"type": "string"}},
    "required": ["dpid"],
}

POLICY_SCHEMA = {"type": "object"}
FLOW_SCHEMA = {"type": "object"}

SCHEMAS = {
    "host": HOST_SCHEMA,
    "switch": SWITCH_SCHEMA,
    "switche": SWITCH_SCHEMA,
    "policy": POLICY_SCHEMA,
    "flow": FLOW_SCHEMA,
}
