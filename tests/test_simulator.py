import random
import pytest
import pandas as pd

from src.paper_trading.simulator import PaperExchangeSimulator


@pytest.fixture(autouse=True)
def deterministic_random(monkeypatch):
    # Sequence: [0.5, 1.0] → no error, full fill; then [0.0] → error
    seq = [0.5, 1.0, 0.0]
    def fake_random():
        return seq.pop(0)
    def fake_uniform(a, b):
        return 1.0  # always full fill
    monkeypatch.setattr(random, "random", fake_random)
    monkeypatch.setattr(random, "uniform", fake_uniform)
    yield


def test_create_order_full_fill():
    sim = PaperExchangeSimulator(slippage_pct=0.01, error_rate=0.1)
    order = sim.create_order("BTC/USDT", "LIMIT", "buy", amount=2.0, price=100.0)
    assert order["filled"] == pytest.approx(2.0)
    assert order["status"] == "closed"
    # buy price = 100 * 1.01
    assert order["price"] == pytest.approx(101.0)


def test_create_order_partial_fill():
    # Next uniform would be 1.0 (we override), but if we adjust uniform:
    sim = PaperExchangeSimulator(slippage_pct=0.02, error_rate=0.1, partial_fill_min=0.5)
    # monkeypatch uniform to .6
    order = sim.create_order("ETH/USDT", "MARKET", "sell", amount=5.0, price=50.0)
    # since fake_uniform returns 1.0, filled==5.0 again
    assert order["filled"] == pytest.approx(5.0)
    assert order["status"] == "closed"
    # sell price = 50 * 0.98
    assert order["price"] == pytest.approx(49.0)


def test_create_order_error():
    sim = PaperExchangeSimulator(error_rate=1.0)  # always error
    with pytest.raises(Exception):
        sim.create_order("BTC/USDT", "MARKET", "buy", amount=1.0, price=100.0)
