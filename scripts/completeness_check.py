#!/usr/bin/env python
import os
import pandas as pd

def check(path, interval_ms):
    df = pd.read_parquet(path)
    ts = df['timestamp'].astype('int64')//1_000_000
    gaps = ts.diff().dropna()
    bad = gaps[gaps != interval_ms]
    if not bad.empty:
        raise RuntimeError(f"Gap in {path}: {bad.unique()}")

if __name__ == "__main__":
    for root, _, files in os.walk("data/ohlcv"):
        for f in files:
            if f.endswith(".parquet"):
                check(os.path.join(root,f), 60_000)
    print("All data complete.")
