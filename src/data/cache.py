"""
Caching & rate-limit control layer for CCXT exchanges.
"""

import ccxt
import time
import threading
import os
from typing import Any, Callable, Dict, Tuple
from functools import wraps

# Simple TTL cache decorator
def ttl_cache(ttl_seconds: int):
    def decorator(func: Callable):
        cache: Dict[Tuple, Tuple[Any, float]] = {}
        lock = threading.Lock()

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Key includes function name, args, kwargs
            key = (func.__name__, args, tuple(sorted(kwargs.items())))
            now = time.time()
            with lock:
                if key in cache:
                    result, expires = cache[key]
                    if now < expires:
                        return result
                result = func(*args, **kwargs)
                cache[key] = (result, now + ttl_seconds)
                return result

        return wrapper
    return decorator

class RateLimiter:
    """
    Ensures we wait at least `rate_limit_ms` between calls.
    """
    def __init__(self, rate_limit_ms: int):
        self.interval = rate_limit_ms / 1000.0
        self.lock = threading.Lock()
        self.last_time = 0.0

    def __call__(self):
        with self.lock:
            now = time.time()
            wait = self.interval - (now - self.last_time)
            if wait > 0:
                time.sleep(wait)
            self.last_time = time.time()

# One RateLimiter per exchange
_rate_limiters: Dict[str, RateLimiter] = {}

def get_rate_limiter(exchange_id: str) -> RateLimiter:
    if exchange_id not in _rate_limiters:
        exchange_cls = getattr(ccxt, exchange_id)
        exch = exchange_cls({"enableRateLimit": True})
        _rate_limiters[exchange_id] = RateLimiter(exch.rateLimit)
    return _rate_limiters[exchange_id]

@ttl_cache(ttl_seconds=300)
def fetch_markets(exchange_id: str) -> Any:
    """
    Fetch and cache exchange markets (5-minute TTL).
    """
    limiter = get_rate_limiter(exchange_id)
    limiter()
    exchange_cls = getattr(ccxt, exchange_id)
    exch = exchange_cls({"enableRateLimit": True})
    return exch.fetch_markets()

@ttl_cache(ttl_seconds=10)
def fetch_ticker(exchange_id: str, symbol: str) -> Any:
    """
    Fetch and cache ticker data (10-second TTL).
    """
    limiter = get_rate_limiter(exchange_id)
    limiter()
    exchange_cls = getattr(ccxt, exchange_id)
    exch = exchange_cls({"enableRateLimit": True})
    return exch.fetch_ticker(symbol)

@ttl_cache(ttl_seconds=10)
def fetch_order_book(exchange_id: str, symbol: str, limit: int = None) -> Any:
    """
    Fetch and cache order book data (10-second TTL).
    """
    limiter = get_rate_limiter(exchange_id)
    limiter()
    exchange_cls = getattr(ccxt, exchange_id)
    exch = exchange_cls({"enableRateLimit": True})
    return exch.fetch_order_book(symbol, limit)
