class Channel:
    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        *,
        transport=None,
        ssl=None
    ):
        self.transport = transport
        self.host = host
        self.port = port
        self.ssl = ssl

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def request(self, method_name: str, request, *, metadata=None):
        if not self.transport:
            raise RuntimeError("no transport")
        return await self.transport.call(method_name, request, metadata or {})
