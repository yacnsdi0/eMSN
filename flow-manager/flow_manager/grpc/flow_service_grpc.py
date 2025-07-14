from __future__ import annotations
from .flow_service_pb2 import FlowRequest, FlowAck


class FlowServiceBase:
    async def InstallFlow(
        self, request: FlowRequest, *, metadata: dict | None = None
    ) -> FlowAck:
        raise NotImplementedError()

    async def DeleteFlow(
        self, request: FlowRequest, *, metadata: dict | None = None
    ) -> FlowAck:
        raise NotImplementedError()


class FlowServiceStub:
    def __init__(self, channel) -> None:
        self.channel = channel

    async def InstallFlow(
        self,
        request: FlowRequest,
        *,
        metadata: dict | None = None,
        timeout: float | None = None,
    ) -> FlowAck:
        return await self.channel.request("InstallFlow", request, metadata=metadata)

    async def DeleteFlow(
        self,
        request: FlowRequest,
        *,
        metadata: dict | None = None,
        timeout: float | None = None,
    ) -> FlowAck:
        return await self.channel.request("DeleteFlow", request, metadata=metadata)
