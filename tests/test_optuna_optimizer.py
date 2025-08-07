import json
import pandas as pd
import tempfile
import os

import pytest
import optuna

from src.strategy.optuna_optimizer import run_optimization


@pytest.fixture
def sample_df() -> pd.DataFrame:
    # Create synthetic data with a known up‐down pattern
    dates = pd.date_range("2021-01-01", periods=50, freq="D")
    prices = list(range(25)) + list(range(25, 0, -1))
    df = pd.DataFrame({
        "timestamp": dates,
        "open": prices,
        "high": prices,
        "low": prices,
        "close": prices,
        "volume": [1.0] * len(prices),
    })
    return df


def test_run_optimization_creates_storage_file(sample_df, tmp_path, monkeypatch):
    # Force a small number of trials for speed
    output = tmp_path / "study.json"
    best = run_optimization(sample_df, n_trials=5, storage_path=str(output))

    assert isinstance(best, dict)
    # JSON file exists and content matches best
    assert output.exists()
    data = json.loads(output.read_text())
    assert data == best
    # Keys should include our param names
    assert "span_short" in best and "span_long" in best and "size" in best


def test_find_reasonable_params(sample_df):
    # Run a minimal study
    best = run_optimization(sample_df, n_trials=3, storage_path="unused.json")
    # All params in expected ranges
    assert 2 <= best["span_short"] < best["span_long"] <= 20
    assert 0.1 <= best["size"] <= 1.0
