class exceptions:
    class ConnectionFailedError(Exception):
        pass


class Etcd3Client:

    def __init__(self):
        self.store = {}

    def put(self, key, value, metadata=None):
        self.store[key] = value

    def get(self, key, metadata=None):
        return self.store.get(key), None

    def delete(self, key, metadata=None):
        self.store.pop(key, None)

    class _Compare:
        def __init__(self, key):
            self.key = key

        def __eq__(self, other):  # noqa: D105 - simple stub
            return ("value", self.key, other)

    class _Transactions:
        def value(self, key):
            return Etcd3Client._Compare(key)

        @staticmethod
        def put(key, value):
            return ("put", key, value)

    transactions = _Transactions()

    def transaction(self, compare=None, success=None, failure=None):
        if compare and compare[0][0] == "value":
            key = compare[0][1]
            if self.store.get(key) != compare[0][2]:
                return False
        if success and success[0][0] == "put":
            self.store[success[0][1]] = success[0][2]
        return True
