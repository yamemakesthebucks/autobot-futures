import time
import pytest
import ccxt

from src.data.cache import (
    fetch_markets,
    fetch_ticker,
    fetch_order_book,
    RateLimiter
)

class DummyExchange:
    def __init__(self, params):
        # Simulate 200ms rate limit
        self.rateLimit = 200
    def fetch_markets(self):
        return ["BTC/USDT", "ETH/USDT"]
    def fetch_ticker(self, symbol):
        return {"symbol": symbol, "price": 123.45}
    def fetch_order_book(self, symbol, limit):
        return {"symbol": symbol, "bids": [], "asks": [], "limit": limit}

@pytest.fixture(autouse=True)
def patch_ccxt(monkeypatch):
    # Redirect ccxt.binance to our DummyExchange
    monkeypatch.setattr(ccxt, "binance", lambda params: DummyExchange(params))

def test_fetch_markets():
    m1 = fetch_markets("binance")
    m2 = fetch_markets("binance")
    assert isinstance(m1, list)
    assert m1 == m2  # cached

def test_fetch_ticker():
    t1 = fetch_ticker("binance", "BTC/USDT")
    t2 = fetch_ticker("binance", "BTC/USDT")
    assert isinstance(t1, dict)
    assert t1 == t2  # cached

def test_fetch_order_book():
    ob = fetch_order_book("binance", "ETH/USDT", limit=5)
    assert ob["symbol"] == "ETH/USDT"
    assert ob["limit"] == 5

def test_rate_limiter_sleep():
    limiter = RateLimiter(rate_limit_ms=300)
    start = time.time()
    limiter()  # first call no delay
    limiter()  # second call delays ~300ms
    elapsed = time.time() - start
    assert elapsed >= 0.3
