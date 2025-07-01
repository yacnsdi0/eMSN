class ClientSession:
    def __init__(self, *a, **kw):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def post(self, url, json=None):
        class Resp:
            status = 200
            async def text(self):
                return ''
        return Resp()
