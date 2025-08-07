from typing import List, Dict
import pandas as pd
from src.strategy.base_strategy import BaseStrategy


class ExampleMomentumStrategy(BaseStrategy):
    """
    Simple EMA crossover momentum strategy.
    """

    def __init__(
        self,
        size: float = 1.0,
        span_short: int = 20,
        span_long: int = 50
    ):
        """
        Args:
            size: Fixed trade size for each signal.
            span_short: Lookback span for short EMA.
            span_long:  Lookback span for long EMA.
        """
        self.size = size
        self.span_short = span_short
        self.span_long = span_long

    def generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """
        Generate buy/sell signals when the short-EMA crosses the long-EMA.

        Args:
            df: DataFrame with columns ['timestamp','open','high','low','close','volume'],
                or indexed by timestamp with index name 'timestamp'.

        Returns:
            List of dicts:
              {'timestamp': pd.Timestamp, 'side': 'buy'/'sell', 'size': float}
        """
        # Work on a copy
        data = df.copy()

        # If the DataFrame was re-indexed (timestamp dropped), restore the column
        if "timestamp" not in data.columns:
            data["timestamp"] = data.index

        # Normalize timestamp column and set as index (retain column)
        data["timestamp"] = pd.to_datetime(data["timestamp"])
        data.set_index("timestamp", inplace=True, drop=False)

        # Compute EMAs
        data["ema_short"] = data["close"].ewm(span=self.span_short, adjust=False).mean()
        data["ema_long"]  = data["close"].ewm(span=self.span_long, adjust=False).mean()

        signals: List[Dict] = []
        prev = data.iloc[0]

        # Iterate through rows to detect crossovers
        for current in data.iloc[1:].itertuples():
            prev_short = prev.ema_short
            prev_long  = prev.ema_long
            curr_short = current.ema_short
            curr_long  = current.ema_long
            ts = current.Index  # pd.Timestamp

            # Golden cross → buy
            if prev_short < prev_long and curr_short > curr_long:
                signals.append({
                    "timestamp": ts,
                    "side": "buy",
                    "size": self.size
                })
            # Death cross → sell
            elif prev_short > prev_long and curr_short < curr_long:
                signals.append({
                    "timestamp": ts,
                    "side": "sell",
                    "size": self.size
                })

            prev = data.loc[ts]

        return signals
