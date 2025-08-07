import pandas as pd
import pytest

from src.backtesting.slippage import (
    apply_slippage,
    apply_latency,
    simulate_fill_orders
)


def test_apply_slippage_buy():
    assert apply_slippage(100.0, 0.01, "buy") == 101.0


def test_apply_slippage_sell():
    assert apply_slippage(100.0, 0.02, "sell") == 98.0


def test_apply_slippage_invalid_side():
    with pytest.raises(ValueError):
        apply_slippage(100.0, 0.01, "hold")


def test_apply_latency():
    ts = pd.Timestamp("2021-01-01T00:00:00Z")
    new_ts = apply_latency(ts, 500)
    assert new_ts == ts + pd.Timedelta(milliseconds=500)


def test_simulate_fill_orders():
    orders = [
        {
            "timestamp": pd.Timestamp("2021-01-01T00:00:00Z"),
            "price": 100.0,
            "side": "buy"
        }
    ]
    fills = simulate_fill_orders(orders, slippage_pct=0.01, latency_ms=1000)
    assert len(fills) == 1
    fill = fills[0]
    assert fill["price"] == 101.0
    assert fill["timestamp"] == pd.Timestamp("2021-01-01T00:00:01Z")
