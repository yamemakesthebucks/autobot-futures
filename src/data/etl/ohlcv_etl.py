"""
ETL module: Prefect flow and tasks for OHLCV data ingestion.
"""

import os
import subprocess
import logging
import ccxt
import pandas as pd

from datetime import datetime, timedelta
from prefect import flow, task

# Configure module‐level logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@task(retries=2, retry_delay_seconds=10)
def fetch_ohlcv(
    exchange_id: str,
    symbol: str,
    timeframe: str,
    since: int,
    limit: int = 500
) -> pd.DataFrame:
    """
    Fetch OHLCV data from an exchange via CCXT.
    """
    logger.info(f"Fetching OHLCV: {exchange_id} {symbol} {timeframe} since {since}")
    exchange_cls = getattr(ccxt, exchange_id)
    exchange = exchange_cls({"enableRateLimit": True})
    raw = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
    df = pd.DataFrame(raw, columns=[
        "timestamp", "open", "high", "low", "close", "volume"
    ])
    return df


@task
def transform(
    df: pd.DataFrame,
    exchange: str,
    symbol: str,
    timeframe: str
) -> pd.DataFrame:
    """
    Transform raw OHLCV DataFrame to the canonical schema.
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["trade_count"] = None
    df["vwap"] = None
    df["exchange"] = exchange
    df["symbol"] = symbol
    df["timeframe"] = timeframe
    df["source"] = "ccxt"
    df["fetched_at"] = pd.Timestamp.utcnow()

    columns = [
        "timestamp", "open", "high", "low", "close", "volume",
        "trade_count", "vwap", "exchange", "symbol",
        "timeframe", "source", "fetched_at"
    ]
    return df[columns]


@task
def load_to_parquet(
    df: pd.DataFrame,
    output_path: str
) -> None:
    """
    Load DataFrame to Parquet and track it with DVC.
    """
    logger.info(f"Writing Parquet to {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_parquet(output_path, index=False)
    subprocess.run(["dvc", "add", output_path], check=True)
    logger.info(f"Added to DVC: {output_path}")


@flow(name="ohlcv-etl")
def ohlcv_etl_flow(
    exchange_id: str,
    symbol: str,
    timeframe: str,
    lookback_days: int = 1
) -> None:
    """
    Prefect flow that fetches, transforms, and loads OHLCV data.
    """
    now = datetime.utcnow()
    since_ms = int((now - timedelta(days=lookback_days)).timestamp() * 1000)

    df_raw = fetch_ohlcv(exchange_id, symbol, timeframe, since_ms)
    df_clean = transform(df_raw, exchange_id, symbol, timeframe)

    out_dir = (
        f"data/ohlcv/{exchange_id}/"
        f"{symbol.replace('/', '-')}/{timeframe}/"
        f"year={now.year}/month={now.month:02d}/day={now.day:02d}"
    )
    out_path = os.path.join(out_dir, "ohlcv.parquet")
    load_to_parquet(df_clean, out_path)
