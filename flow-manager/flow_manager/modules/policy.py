"""Simple allow/block policy engine."""
from __future__ import annotations

from typing import Any


def allow_flow(flow: dict[str, Any]) -> bool:
    """Always allow flows (placeholder)."""
    return True
