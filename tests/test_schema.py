import datetime
import pytest

from src.data.schema import JSON_SCHEMA, get_partition_path


def test_json_schema_structure():
    # Basic structure checks
    assert isinstance(JSON_SCHEMA, dict)
    assert JSON_SCHEMA["type"] == "object"
    assert "properties" in JSON_SCHEMA
    props = JSON_SCHEMA["properties"]
    for field in ("timestamp", "open", "high", "low", "close", "volume"):
        assert field in props


def test_required_fields():
    required = JSON_SCHEMA["required"]
    for field in (
        "timestamp", "open", "high", "low", "close", "volume",
        "exchange", "symbol", "timeframe", "source", "fetched_at"
    ):
        assert field in required


def test_partition_path():
    dt = datetime.datetime(2021, 3, 5, 12, 30)
    path = get_partition_path("binance", "BTC/USDT", "1m", dt)
    expected = "data/ohlcv/binance/BTC-USDT/1m/year=2021/month=03/day=05"
    assert path == expected
