"""
Ensemble manager to choose the best strategy per regime.
"""

import logging
from typing import Dict
import pandas as pd

from src.strategy.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class EnsembleManager:
    """
    Manages multiple strategies and selects one based on regime performance.
    """

    def __init__(
        self,
        strategies: Dict[str, BaseStrategy],
        performance_data: Dict[str, Dict[str, float]] = None
    ):
        """
        Args:
            strategies: Mapping of strategy names to BaseStrategy instances.
            performance_data: Nested dict {strategy_name: {regime_label: score}}.
                              If None, all scores default to 1.0.
        """
        self.strategies = strategies
        if performance_data is None:
            self.performance_data = {
                name: {"high": 1.0, "low": 1.0} for name in strategies
            }
        else:
            self.performance_data = performance_data

    def select_strategy(self, regimes: pd.Series) -> BaseStrategy:
        """
        Pick the strategy with the highest score for the current regime.

        Args:
            regimes: pd.Series of regime labels ('high'/'low'), indexed by time.

        Returns:
            The chosen BaseStrategy instance.
        """
        current = regimes.iloc[-1]
        logger.info(f"Current regime: {current}")
        best_name = max(
            self.performance_data.keys(),
            key=lambda name: self.performance_data[name].get(current, 0.0)
        )
        logger.info(f"Selected strategy: {best_name}")
        return self.strategies[best_name]
