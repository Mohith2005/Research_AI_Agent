# src/utils/retry.py
import asyncio
from functools import wraps
from typing import Type, Tuple

def async_retry(
    max_attempts: int = 3,
    delays: Tuple[float] = (1, 3, 5),
    exceptions: Tuple[Type[Exception]] = (Exception,)
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise e
                    await asyncio.sleep(delays[attempt])
            return None
        return wrapper
    return decorator