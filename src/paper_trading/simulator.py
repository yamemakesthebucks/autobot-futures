"""
Paper-trading simulator: simulates CCXT exchange behavior with slippage,
partial fills, and error injection.
"""

import random
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PaperExchangeSimulator:
    """
    Simulates a CCXT-like exchange for paper trading purposes.
    """

    def __init__(
        self,
        slippage_pct: float = 0.001,
        error_rate: float = 0.01,
        partial_fill_min: float = 0.5
    ):
        """
        Args:
            slippage_pct: Fractional slippage applied to the fill price.
            error_rate: Probability [0–1] of raising a simulated error on create_order.
            partial_fill_min: Minimum fraction of order that will be filled when partial.
        """
        self.slippage_pct = slippage_pct
        self.error_rate = error_rate
        self.partial_fill_min = partial_fill_min

    def create_order(
        self,
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Simulate placing an order.

        Args:
            symbol: Market symbol, e.g. "BTC/USDT".
            type: Order type, e.g. "MARKET" or "LIMIT".
            side: "buy" or "sell".
            amount: Intended amount.
            price: Limit price (for LIMIT orders) or None for MARKET.

        Returns:
            A dict mimicking CCXT order response with keys:
              - symbol, type, side, amount, filled, price, status

        Raises:
            Exception: Simulated exchange error.
        """
        # Possibly throw a simulated error
        if random.random() < self.error_rate:
            logger.error("Simulated exchange error")
            raise Exception("Simulated exchange error")

        # Determine fill fraction
        frac = random.uniform(self.partial_fill_min, 1.0)
        filled = round(amount * frac, 8)

        # Determine fill price with slippage
        exec_price = price if price is not None else 0.0
        if side == "buy":
            exec_price = exec_price * (1 + self.slippage_pct)
        else:
            exec_price = exec_price * (1 - self.slippage_pct)

        status = "closed" if filled >= amount else "partial"

        logger.info(
            f"Simulated fill for {symbol}: "
            f"{filled}/{amount} @ {exec_price:.8f} ({status})"
        )

        return {
            "symbol": symbol,
            "type": type,
            "side": side,
            "amount": amount,
            "filled": filled,
            "price": exec_price,
            "status": status,
        }
