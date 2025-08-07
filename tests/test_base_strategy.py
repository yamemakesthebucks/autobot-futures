import pytest
import pandas as pd
from src.strategy.base_strategy import BaseStrategy


def test_generate_signals_not_implemented():
    strat = BaseStrategy()
    with pytest.raises(NotImplementedError):
        strat.generate_signals(pd.DataFrame(columns=["timestamp"]))
