"""
Canonical OHLCV JSON Schema and partition path logic.
"""

import datetime
from typing import Dict

JSON_SCHEMA: Dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "OHLCV Candle",
    "type": "object",
    "properties": {
        "timestamp":   {"type": "string", "format": "date-time"},
        "open":        {"type": "number"},
        "high":        {"type": "number"},
        "low":         {"type": "number"},
        "close":       {"type": "number"},
        "volume":      {"type": "number"},
        "trade_count": {"type": ["integer", "null"]},
        "vwap":        {"type": ["number", "null"]},
        "exchange":    {"type": "string"},
        "symbol":      {"type": "string"},
        "timeframe":   {"type": "string"},
        "source":      {"type": "string"},
        "fetched_at":  {"type": "string", "format": "date-time"},
    },
    "required": [
        "timestamp", "open", "high", "low", "close", "volume",
        "exchange", "symbol", "timeframe", "source", "fetched_at"
    ],
    "additionalProperties": False,
}


def get_partition_path(
    exchange: str,
    symbol: str,
    timeframe: str,
    dt: datetime.datetime
) -> str:
    """
    Compute the Parquet partition path for a given exchange/symbol/timeframe and datetime.

    Args:
        exchange: Exchange identifier, e.g. "binance"
        symbol:   Market symbol, e.g. "BTC/USDT"
        timeframe: Candle timeframe, e.g. "1m"
        dt:       A datetime object (UTC)

    Returns:
        A path string like:
        "data/ohlcv/binance/BTC-USDT/1m/year=2025/month=08/day=06"
    """
    sanitized = symbol.replace("/", "-")
    return (
        f"data/ohlcv/{exchange}/{sanitized}/{timeframe}/"
        f"year={dt.year}/month={dt.month:02d}/day={dt.day:02d}"
    )
