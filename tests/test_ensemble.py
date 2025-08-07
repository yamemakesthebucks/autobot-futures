import pandas as pd

import pytest
from src.strategy.ensemble import EnsembleManager


class DummyStrategy:
    def __init__(self, name):
        self.name = name


@pytest.fixture
def strategies():
    return {
        "A": DummyStrategy("A"),
        "B": DummyStrategy("B")
    }


@pytest.fixture
def performance_data():
    return {
        "A": {"high": 10.0, "low": 1.0},
        "B": {"high": 2.0,  "low": 5.0}
    }


def test_select_strategy_high_regime(strategies, performance_data):
    manager = EnsembleManager(strategies, performance_data)
    regimes = pd.Series(["low", "high", "high"])
    selected = manager.select_strategy(regimes)
    assert isinstance(selected, DummyStrategy)
    assert selected.name == "A"


def test_select_strategy_low_regime(strategies, performance_data):
    manager = EnsembleManager(strategies, performance_data)
    regimes = pd.Series(["high", "low", "low"])
    selected = manager.select_strategy(regimes)
    assert selected.name == "B"
