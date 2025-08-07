import pandas as pd
from datetime import datetime, timedelta
import pytest

from src.strategy.example_momentum import ExampleMomentumStrategy


@pytest.fixture
def sample_df() -> pd.DataFrame:
    # Create 8 points rising then falling to force at least one crossover
    start = datetime(2021, 1, 1)
    dates = [start + timedelta(days=i) for i in range(8)]
    closes = [1, 2, 3, 4, 5, 4, 3, 2]
    return pd.DataFrame({
        "timestamp": dates,
        "open": closes,
        "high": closes,
        "low": closes,
        "close": closes,
        "volume": [1.0] * len(dates),
    })


def test_signals_emerge(sample_df):
    strat = ExampleMomentumStrategy(size=10.0, span_short=3, span_long=5)
    signals = strat.generate_signals(sample_df)

    # Expect at least one signal (buy or sell)
    assert len(signals) >= 1

    # Each signal must be valid
    for sig in signals:
        assert sig["side"] in {"buy", "sell"}
        assert sig["size"] == 10.0
        assert isinstance(sig["timestamp"], pd.Timestamp)


def test_no_false_signals_on_flat(sample_df):
    flat = sample_df.copy()
    flat["close"] = 100.0
    strat = ExampleMomentumStrategy(size=1.0, span_short=3, span_long=5)
    signals = strat.generate_signals(flat)
    assert signals == []
