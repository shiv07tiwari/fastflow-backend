import functools
from hashlib import sha256
import asyncio

import redis
from redis import asyncio as aioredis


async def is_redis_available(r):
    try:
        return await r.ping()  # Try pinging the Redis server
    except (redis.exceptions.ConnectionError, redis.exceptions.BusyLoadingError):
        return False


try:
    # Initialize Redis client
    async_redis_client = aioredis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True  # Automatically decoding responses to Python strings
    )
    sync_redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True  # Automatically decoding responses to Python strings
    )
except Exception as e:
    print(f"Error connecting to Redis: {e}")
    async_redis_client = None
    sync_redis_client = None


def cache_response(timeout=86400):  # Default timeout set to 1 day (in seconds)
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not await is_redis_available(async_redis_client):
                return await func(*args, **kwargs)

            # Generate a unique cache key based on function name and parameters
            key_base = f"{func.__name__}:{args}-{kwargs}"
            cache_key = 'cache:' + sha256(key_base.encode('utf-8')).hexdigest()

            # Try to get cached response
            cached = await async_redis_client.get(cache_key)
            if cached is not None:
                print(f"Cache hit - {cache_key}")
                return cached

            # Calculate result and cache it
            result = await func(*args, **kwargs)
            if result:
                await async_redis_client.setex(cache_key, timeout, result)
                print(f"Cache set - {cache_key}")
            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not is_redis_available(sync_redis_client):
                return func(*args, **kwargs)

            # Generate a unique cache key based on function name and parameters
            key_base = f"{func.__name__}:{args}-{kwargs}"
            cache_key = 'cache:' + sha256(key_base.encode('utf-8')).hexdigest()

            # Try to get cached response
            cached = sync_redis_client.get(cache_key)
            if cached is not None:
                print(f"Cache hit - {cache_key}")
                return cached

            # Calculate result and cache it
            result = func(*args, **kwargs)
            if result:
                sync_redis_client.setex(cache_key, timeout, result)
                print(f"Cache set - {cache_key}")
            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
