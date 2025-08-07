import os
import subprocess
import pandas as pd
import pytest

from src.data.etl.ohlcv_etl import (
    fetch_ohlcv,
    transform,
    load_to_parquet,
    ohlcv_etl_flow,
)

class DummyExchange:
    def __init__(self, params):
        pass

    def fetch_ohlcv(self, symbol, timeframe, since, limit):
        return [[since, 1.0, 2.0, 0.5, 1.5, 100.0]]


@pytest.fixture(autouse=True)
def patch_ccxt(monkeypatch):
    import ccxt
    monkeypatch.setattr(ccxt, "binance", lambda params: DummyExchange(params))


def test_fetch_ohlcv_task():
    # Call the underlying function via .fn
    df = fetch_ohlcv.fn("binance", "BTC/USDT", "1m", 1600000000000, 1)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["timestamp", "open", "high", "low", "close", "volume"]
    assert df.iloc[0]["open"] == 1.0


def test_transform_task():
    raw = pd.DataFrame(
        [[1600000000000, 1.0, 2.0, 0.5, 1.5, 100.0]],
        columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df = transform.fn(raw, "binance", "BTC/USDT", "1m")
    expected_cols = [
        "timestamp", "open", "high", "low", "close", "volume",
        "trade_count", "vwap", "exchange", "symbol",
        "timeframe", "source", "fetched_at"
    ]
    assert list(df.columns) == expected_cols
    assert df.iloc[0]["exchange"] == "binance"


def test_load_to_parquet(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: None)
    raw = pd.DataFrame(
        [[pd.Timestamp("2025-01-01"), 1.0, 2.0, 0.5, 1.5, 100.0]],
        columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    out = tmp_path / "test.parquet"
    # Call the task's .fn function
    load_to_parquet.fn(raw, str(out))
    assert out.exists()
    df2 = pd.read_parquet(str(out))
    # Should preserve only the original six columns
    assert list(df2.columns) == ["timestamp", "open", "high", "low", "close", "volume"]


def test_full_flow(tmp_path, monkeypatch):
    # Patch subprocess.run for DVC
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: None)
    # Run the Prefect v2 flow directly
    ohlcv_etl_flow(
        exchange_id="binance",
        symbol="BTC/USDT",
        timeframe="1m",
        lookback_days=0
    )
    # Expect a parquet file under today’s partition
    import datetime
    now = datetime.datetime.utcnow()
    path = (
        f"data/ohlcv/binance/BTC-USDT/1m/"
        f"year={now.year}/month={now.month:02d}/day={now.day:02d}/ohlcv.parquet"
    )
    assert os.path.exists(path)
