import os
import subprocess
import datetime
import pandas as pd
import pytest

from src.data.etl.ohlcv_etl import (
    fetch_ohlcv,
    transform,
    load_to_parquet,
    ohlcv_etl_flow,
)

# -----------------------------------------------------------------------------
# Fixtures to stub out external calls
# -----------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_ccxt(monkeypatch):
    """Stub CCXT exchange creation."""
    import ccxt
    class DummyExchange:
        def __init__(self, params):
            pass

        def fetch_ohlcv(self, symbol, timeframe, since, limit):
            # single OHLCV row
            return [[since, 1.0, 2.0, 0.5, 1.5, 100.0]]
    monkeypatch.setattr(ccxt, "binance", lambda params: DummyExchange(params))

@pytest.fixture(autouse=True)
def patch_subprocess(monkeypatch):
    """Stub subprocess.run for DVC and subprocess.check_output for `file` calls."""
    # DVC calls use subprocess.run → no‐op
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: None)
    # platform.architecture() under the hood calls `file -b <exe>` via check_output
    monkeypatch.setattr(subprocess, "check_output", lambda *args, **kwargs: b"ELF 64-bit")

# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------

def test_fetch_ohlcv_task():
    df = fetch_ohlcv.fn("binance", "BTC/USDT", "1m", 1600000000000, 1)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["timestamp", "open", "high", "low", "close", "volume"]
    assert df.iloc[0]["open"] == 1.0

def test_transform_task():
    raw = pd.DataFrame(
        [[1600000000000, 1.0, 2.0, 0.5, 1.5, 100.0]],
        columns=["timestamp","open","high","low","close","volume"]
    )
    df = transform.fn(raw, "binance", "BTC/USDT", "1m")
    expected = [
        "timestamp","open","high","low","close","volume",
        "trade_count","vwap","exchange","symbol",
        "timeframe","source","fetched_at"
    ]
    assert list(df.columns) == expected
    assert df.iloc[0]["exchange"] == "binance"

def test_load_to_parquet(tmp_path):
    raw = pd.DataFrame(
        [[pd.Timestamp("2025-01-01"),1.0,2.0,0.5,1.5,100.0]],
        columns=["timestamp","open","high","low","close","volume"]
    )
    out = tmp_path / "test.parquet"
    load_to_parquet.fn(raw, str(out))
    assert out.exists()
    df2 = pd.read_parquet(str(out))
    assert list(df2.columns) == ["timestamp","open","high","low","close","volume"]

def test_full_flow(tmp_path):
    # Run the Prefect v2 flow end-to-end
    ohlcv_etl_flow(
        exchange_id="binance",
        symbol="BTC/USDT",
        timeframe="1m",
        lookback_days=0
    )
    now = datetime.datetime.utcnow()
    path = (
        f"data/ohlcv/binance/BTC-USDT/1m/"
        f"year={now.year}/month={now.month:02d}/day={now.day:02d}/ohlcv.parquet"
    )
    assert os.path.exists(path)
