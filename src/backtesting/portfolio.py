"""
Portfolio engine: position sizing and drawdown enforcement.
"""

import logging

logger = logging.getLogger(__name__)


class Portfolio:
    """
    Tracks capital and enforces a maximum drawdown limit.
    """

    def __init__(self, capital: float, max_drawdown: float):
        """
        Args:
            capital: Initial starting capital.
            max_drawdown: Maximum allowed drawdown as fraction (e.g. 0.1 for 10%).
        """
        if capital <= 0:
            raise ValueError("Initial capital must be positive")
        if not 0 <= max_drawdown < 1:
            raise ValueError("max_drawdown must be in [0,1)")

        self.initial_capital: float = capital
        self.capital: float = capital
        self.max_drawdown: float = max_drawdown
        logger.info(f"Portfolio initialized with capital={capital}, max_drawdown={max_drawdown}")

    def position_size(self, price: float, risk_pct: float) -> float:
        """
        Compute position size so that risk_pct * capital is at risk at this price.

        Args:
            price: Current asset price.
            risk_pct: Fraction of capital to risk (e.g. 0.01 for 1%).

        Returns:
            Number of units to trade.
        """
        if price <= 0:
            raise ValueError("Price must be positive")
        if not 0 < risk_pct <= 1:
            raise ValueError("risk_pct must be in (0, 1]")

        risk_amount = self.capital * risk_pct
        size = risk_amount / price
        logger.debug(f"Computed position size={size} for price={price}, risk_pct={risk_pct}")
        return size

    def update(self, pnl: float) -> None:
        """
        Update capital by realized PnL and enforce max drawdown.

        Args:
            pnl: Realized profit (positive) or loss (negative).

        Raises:
            RuntimeError: If capital falls below allowed drawdown threshold.
        """
        prev = self.capital
        self.capital += pnl
        logger.info(f"Portfolio updated by pnl={pnl}: {prev} → {self.capital}")

        floor = self.initial_capital * (1 - self.max_drawdown)
        if self.capital < floor:
            msg = (
                f"Max drawdown breached: capital {self.capital:.2f} "
                f"< floor {floor:.2f}"
            )
            logger.error(msg)
            raise RuntimeError("Max drawdown breached")
