import base64
import json
from typing import Any, Iterable, cast

from . import JWTError


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64json(obj: Any) -> str:
    return _b64(json.dumps(obj).encode())


def _decode_part(part: str) -> Any:
    padding = "=" * (-len(part) % 4)
    return json.loads(base64.urlsafe_b64decode(part + padding))


def encode(payload: dict[str, Any], key: Any, algorithm: str = "ES256") -> str:
    header = {"alg": algorithm, "typ": "JWT"}
    return f"{_b64json(header)}.{_b64json(payload)}.sig"


def decode(
    token: str,
    key: Any,
    algorithms: Iterable[str] | None = None,
    audience: str | None = None,
) -> dict[str, Any]:
    try:
        header_b64, payload_b64, _ = token.split(".")
        payload = cast(dict[str, Any], _decode_part(payload_b64))
    except Exception as exc:  # noqa: BLE001
        raise JWTError("malformed token") from exc
    if audience is not None and payload.get("aud") != audience:
        raise JWTError("invalid audience")
    return payload
