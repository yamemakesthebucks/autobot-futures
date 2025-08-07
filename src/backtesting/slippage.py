"""
Slippage and latency simulation for backtesting.
"""

from typing import Dict, List
import pandas as pd

def apply_slippage(
    price: float,
    slippage_pct: float,
    side: str
) -> float:
    """
    Apply slippage to a quoted price.

    Args:
        price: The raw fill price.
        slippage_pct: e.g. 0.01 for 1% slippage.
        side: 'buy' or 'sell'.

    Returns:
        Adjusted price: higher on buy, lower on sell.

    Raises:
        ValueError for invalid side.
    """
    if side not in ("buy", "sell"):
        raise ValueError("side must be 'buy' or 'sell'")
    if side == "buy":
        return price * (1 + slippage_pct)
    else:
        return price * (1 - slippage_pct)


def apply_latency(
    timestamp: pd.Timestamp,
    latency_ms: int
) -> pd.Timestamp:
    """
    Apply a fixed latency to a timestamp.

    Args:
        timestamp: Original event time.
        latency_ms: Latency in milliseconds.

    Returns:
        New Timestamp delayed by latency_ms.
    """
    return timestamp + pd.Timedelta(milliseconds=latency_ms)


def simulate_fill_orders(
    orders: List[Dict],
    slippage_pct: float,
    latency_ms: int
) -> List[Dict]:
    """
    Given a list of raw orders, simulate fills with slippage & latency.

    Each order dict must contain:
      - 'timestamp': pd.Timestamp
      - 'price': float
      - 'side': 'buy' or 'sell'

    Returns:
        A new list of fill dicts with adjusted 'price' and 'timestamp'.
    """
    fills: List[Dict] = []
    for order in orders:
        adj_price = apply_slippage(order["price"], slippage_pct, order["side"])
        adj_ts = apply_latency(order["timestamp"], latency_ms)
        fill = order.copy()
        fill["price"] = adj_price
        fill["timestamp"] = adj_ts
        fills.append(fill)
    return fills
