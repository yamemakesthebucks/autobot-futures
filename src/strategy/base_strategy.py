from typing import List, Dict
import pandas as pd


class BaseStrategy:
    """
    Base interface for all trading strategies. Subclasses must implement `generate_signals`.
    """
    def generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """
        Generate a list of trading signals from OHLCV data.

        Args:
            df: A pandas DataFrame with at least a 'timestamp' column.

        Returns:
            A list of signals, each a dict with keys:
              - 'timestamp': pd.Timestamp of the signal
              - 'side': 'buy' or 'sell'
              - 'size': float position size
        """
        raise NotImplementedError("Subclasses must implement generate_signals")
