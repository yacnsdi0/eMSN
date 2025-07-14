"""Flow installer using Ryu REST API."""

from __future__ import annotations

import uuid

import httpx

from ..config import Settings


settings = Settings()
_CLIENT = httpx.AsyncClient(timeout=2)


def _build_of_entry(drop: bool, match: dict) -> dict:
    entry = {"priority": 1, "match": match}
    if drop:
        entry["actions"] = []
    return entry


async def _post(action: str, data: dict) -> httpx.Response:
    resp = await _CLIENT.post(
        f"{settings.ryu_rest}/stats/flowentry/{action}", json=data
    )
    if resp.status_code != 200:
        raise RuntimeError("ryu error")
    return resp


async def add_drop_rule(dpid: str, match_dict: dict) -> str:
    flow_id = uuid.uuid4().hex
    entry = _build_of_entry(True, match_dict) | {"dpid": dpid, "id": flow_id}
    await _post("add", entry)
    return flow_id


async def add_forward_rule(
    dpid: str, in_port: int, out_port: int, match_dict: dict
) -> str:
    flow_id = uuid.uuid4().hex
    match = match_dict | {"in_port": in_port}
    entry = _build_of_entry(False, match) | {
        "dpid": dpid,
        "id": flow_id,
        "actions": [{"type": "OUTPUT", "port": out_port}],
    }
    await _post("add", entry)
    return flow_id


async def delete_rule(flow_id: str) -> None:
    await _post("delete", {"id": flow_id})


async def modify_rule(flow_id: str, new_match: dict) -> None:
    await _post("modify", {"id": flow_id, "match": new_match})
