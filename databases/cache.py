import functools
from hashlib import sha256
import redis

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True  # Automatically decoding responses to Python strings
)


def cache_response(timeout=86400):  # Default timeout set to 1 day (in seconds)
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a unique cache key based on function name and parameters
            key_base = f"{func.__name__}:{args}-{kwargs}"
            cache_key = 'cache:' + sha256(key_base.encode('utf-8')).hexdigest()

            # Try to get cached response
            cached = redis_client.get(cache_key)
            if cached is not None:
                print(f"Cache hit - {cache_key}")
                return cached

            # Calculate result and cache it
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, timeout, result)
            print(f"Cache set - {cache_key}")
            return result

        return wrapper

    return decorator
