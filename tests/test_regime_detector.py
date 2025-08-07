import pandas as pd
import pytest

from src.strategy.regime_detector import detect_volatility_regime


def test_detect_volatility_regime_low_high():
    # Build closes that are flat then volatile
    closes = [1, 1, 1, 5, 5, 5]
    df = pd.DataFrame({"close": closes})
    regimes = detect_volatility_regime(df, window=3, threshold=1.0)

    # First 3 std=0 → 'low', next two windows 'high', final window std=0 → 'low'
    expected = ["low", "low", "low", "high", "high", "low"]
    assert list(regimes) == expected
    assert regimes.index.equals(df.index)


def test_missing_close_column():
    df = pd.DataFrame({"open": [1, 2, 3]})
    with pytest.raises(ValueError):
        detect_volatility_regime(df, window=2, threshold=0.5)
