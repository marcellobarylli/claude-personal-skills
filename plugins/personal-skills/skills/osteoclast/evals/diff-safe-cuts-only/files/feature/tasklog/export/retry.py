"""Retry helper for resilient exports."""
import functools
import time


def with_retry(attempts=3, backoff=0.05):
    """Retry the wrapped function on any exception, with linear backoff."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_error = exc
                    if attempt < attempts:
                        time.sleep(backoff * attempt)
            raise last_error

        return wrapper

    return decorator
