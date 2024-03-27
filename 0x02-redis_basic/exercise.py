#!/usr/bin/env python3
"""Exercise for Redis"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator that counts how many times methods
    of the Cache class are called
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and
    outputs for a particular function
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        key = method.__qualname__
        input = str(args)
        self._redis.rpush("{}:inputs".format(key), input)

        output = str(method(self, *args, **kwargs))
        self._redis.rpush("{}:outputs".format(key), output)

        return output
    return wrapper


def replay(method: Callable):
    """
    Display the history of calls of a particular function
    """
    r = redis.Redis()
    key = method.__qualname__
    count = r.get(key).decode("utf-8")
    inputs = r.lrange("{}:inputs".format(key), 0, -1)
    outputs = r.lrange("{}:outputs".format(key), 0, -1)

    print("{} was called {} times:".format(key, count))

    for i, o in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(key, i.decode("utf-8"),
                                     o.decode("utf-8")))


class Cache:
    """Cache class"""
    def __init__(self):
        """Constructor"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in redis"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        """Get data from redis"""
        data = self._redis.get(key)
        if fn:
            return fn(data)
        else:
            return data

    def get_str(self, key: str) -> str:
        """Convert bytes to str"""
        return self.get(key, str)

    def get_int(self, key: str) -> int:
        """Convert bytes to int"""
        return self.get(key, int)
