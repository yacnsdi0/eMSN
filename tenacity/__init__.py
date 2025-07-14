class RetryError(Exception):
    pass


def retry(stop: int | None = None, wait: float | None = None):
    attempts = stop or 1

    def decorator(fn):
        def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for _ in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:  # pragma: no cover - testing stub
                    last_exc = exc
            raise RetryError() from last_exc

        return wrapper

    return decorator


def stop_after_attempt(n: int) -> int:
    return n


def wait_exponential(multiplier: float = 1.0) -> float:
    return multiplier
