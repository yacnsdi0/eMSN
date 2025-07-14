class GRPCError(Exception):
    def __init__(self, status, message: str = "") -> None:
        super().__init__(message or status.name)
        self.status = status
