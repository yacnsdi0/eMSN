class Etcd3Client:
    def __init__(self, host=None, port=None, ca_cert=None, cert_cert=None, cert_key=None):
        self.store = {}
    def put(self, key, value):
        self.store[key] = value
    def get(self, key):
        return self.store.get(key), None
