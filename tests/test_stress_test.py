import pandas as pd
import pytest

from src.backtesting.stress_test import (
    monte_carlo_returns,
    simulate_pnl,
    inject_black_swan
)


def test_monte_carlo_returns_shape():
    returns = pd.Series([0.01, -0.02, 0.03])
    sims = monte_carlo_returns(returns, n_sims=10, seed=42)
    assert sims.shape == (3, 10)
    assert list(sims.index) == list(returns.index)


def test_simulate_pnl():
    # Two sims: first constant 0%, second +10% each period
    df = pd.DataFrame({
        0: [0.0, 0.0, 0.0],
        1: [0.1, 0.1, 0.1]
    }, index=[0, 1, 2])
    finals = simulate_pnl(df, initial_capital=100.0)
    assert pytest.approx(finals.loc[0], rel=1e-6) == 100.0
    assert pytest.approx(finals.loc[1], rel=1e-6) == 100.0 * (1.1**3)


def test_inject_black_swan():
    idx = pd.date_range("2021-01-01", periods=3, freq="D")
    returns = pd.Series([0.0, 0.0, 0.0], index=idx)
    shocked = inject_black_swan(returns, shock_pct=-0.5, on_index=idx[1])
    assert shocked.loc[idx[1]] == pytest.approx(-0.5)
    # Other entries unchanged
    assert shocked.loc[idx[0]] == pytest.approx(0.0)
    assert shocked.loc[idx[2]] == pytest.approx(0.0)


def test_inject_black_swan_keyerror():
    returns = pd.Series([0.0], index=[pd.Timestamp("2021-01-01")])
    with pytest.raises(KeyError):
        inject_black_swan(returns, shock_pct=-0.5, on_index=pd.Timestamp("2021-01-02"))
