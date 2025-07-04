import json
from functools import wraps
from hashlib import sha256
from app.cache import redis_client


def cache_response(ttl=60):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key_data = f"{fn.__name__}:{json.dumps(kwargs, sort_keys=True)}"
            cache_key = sha256(key_data.encode()).hexdigest()

            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            result = fn(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result

        return wrapper

    return decorator
