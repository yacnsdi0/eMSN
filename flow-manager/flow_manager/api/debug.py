from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class DebugResponse(BaseModel):
    jwt: dict | None
    client_cert_cn: str


@router.get("/authz/debug", response_model=DebugResponse)
async def debug(request: Request) -> DebugResponse:
    return DebugResponse(
        jwt=getattr(request.state, "jwt_payload", None),
        client_cert_cn=getattr(request.state, "client_cert_cn", "n/a"),
    )
