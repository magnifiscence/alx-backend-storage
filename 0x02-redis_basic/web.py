#!/usr/bin/env python3
"""Web module"""
import redis
import requests
from functools import wraps


def cache_and_track(func):
    """
    Decorator that takes a single method
    and returns a single method
    """
    @wraps(func)
    def wrapper(url):
        """Wrapper function"""
        redis_store = redis.Redis()
        res_key = f'result:{url}'
        req_key = f'count:{url}'
        result = redis_store.get(res_key)
        if result is not None:
            redis_store.incr(req_key)
            return result.decode('utf-8')
        result = func(url)
        redis_store.setex(res_key, 10, result)
        redis_store.incr(req_key)
        return result
    return wrapper


@cache_and_track
def get_page(url: str) -> str:
    """
    Gets the HTML content of a particular URL
    and returns it
    """
    return requests.get(url).content.decode('utf-8')
