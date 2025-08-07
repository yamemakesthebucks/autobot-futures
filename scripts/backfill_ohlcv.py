#!/usr/bin/env python
import os
from datetime import datetime, timedelta
from prefect import flow, task, get_run_logger
from src.data.etl.ohlcv_etl import fetch_ohlcv, transform, load_to_parquet

@flow(name="backfill-ohlcv")
def backfill_ohlcv():
    exchange = os.getenv("EXCHANGE_ID", "binance")
    symbol   = os.getenv("SYMBOL", "BTC/USDT")
    tf       = os.getenv("TIMEFRAME", "1m")
    start = datetime.fromisoformat(os.getenv("START_DATE"))
    now = datetime.utcnow()
    step = int(os.getenv("BATCH_DAYS")) * 24*60*60*1000

    current_ms = int(start.timestamp()*1000)
    end_ms = int(now.timestamp()*1000)
    while current_ms < end_ms:
        df = fetch_ohlcv(exchange, symbol, tf, current_ms)
        dfc = transform(df, exchange, symbol, tf)
        dt = datetime.utcfromtimestamp(current_ms/1000)
        path = f"data/ohlcv/{exchange}/{symbol.replace('/','-')}/{tf}/year={dt.year}/month={dt.month:02d}/day={dt.day:02d}/ohlcv_{dt:%Y%m%d}.parquet"
        load_to_parquet(dfc, path)
        current_ms += step

if __name__ == "__main__":
    backfill_ohlcv()
