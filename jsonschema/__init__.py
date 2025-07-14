from typing import Any


class ValidationError(Exception):
    """Stubbed validation error."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def validate(instance: Any, schema: Any) -> None:
    props = schema.get("properties", {}) if isinstance(schema, dict) else {}
    if "mac" in props:
        mac = instance.get("mac") if isinstance(instance, dict) else None
        if not isinstance(mac, str) or ":" not in mac:
            raise ValidationError("invalid mac")
    if "dpid" in props:
        dpid = instance.get("dpid") if isinstance(instance, dict) else None
        if not isinstance(dpid, str):
            raise ValidationError("invalid dpid")
