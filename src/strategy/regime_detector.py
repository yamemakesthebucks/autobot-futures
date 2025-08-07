"""
Detect market regimes based on rolling volatility.
"""

import logging
from typing import List
import pandas as pd

logger = logging.getLogger(__name__)


def detect_volatility_regime(
    df: pd.DataFrame,
    window: int,
    threshold: float
) -> pd.Series:
    """
    Compute a volatility regime series from price data.

    Args:
        df: DataFrame containing at least a 'close' column.
        window: Rolling window size (in periods) for standard deviation.
        threshold: Volatility threshold; std >= threshold → 'high', else 'low'.

    Returns:
        pd.Series of regime labels ('high' or 'low'), indexed same as df.
    """
    if "close" not in df.columns:
        raise ValueError("DataFrame must contain a 'close' column")

    logger.info(f"Computing rolling std over window={window}")
    vols = df["close"].rolling(window=window).std().fillna(0.0)
    regimes: List[str] = []
    for v in vols:
        regimes.append("high" if v >= threshold else "low")

    series = pd.Series(regimes, index=df.index)
    logger.info("Regime detection complete")
    return series
