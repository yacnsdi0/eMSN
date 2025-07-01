class Response:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
    def json(self):
        return self._json

class Client:
    def __init__(self, app=None, base_url="http://testserver"):
        self.app = app
        self.base_url = base_url
    def request(self, method, url, **kwargs):
        return Response()

