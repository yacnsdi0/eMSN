class MemoryTransport:
    def __init__(self, service):
        self.service = service

    async def call(self, method_name: str, request, metadata: dict):
        handler = getattr(self.service, method_name)
        return await handler(request, metadata=metadata)
