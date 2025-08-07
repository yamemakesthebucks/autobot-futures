"""
Failure-mode drills for the paper-trading simulator.
"""

import logging
from typing import List, Dict, Any

from src.paper_trading.simulator import PaperExchangeSimulator

logger = logging.getLogger(__name__)


def drill_exchange_down(
    simulator: PaperExchangeSimulator,
    order: Dict[str, Any],
    attempts: int = 3
) -> bool:
    """
    Attempt to place an order multiple times until success or exhaust attempts.

    Args:
        simulator: PaperExchangeSimulator instance.
        order: Dict with keys matching create_order args.
        attempts: Max tries before giving up.

    Returns:
        True if any attempt succeeded, False otherwise.
    """
    for i in range(1, attempts + 1):
        try:
            result = simulator.create_order(**order)
            logger.info(f"Drill success on attempt {i}: {result}")
            return True
        except Exception as e:
            logger.warning(f"Drill attempt {i} failed: {e}")
    logger.error(f"Drill failed after {attempts} attempts")
    return False


def drill_partial_fill_analysis(
    simulator: PaperExchangeSimulator,
    orders: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Place each order and record the fill ratio or error.

    Args:
        simulator: PaperExchangeSimulator instance.
        orders: List of order-dicts for create_order.

    Returns:
        List of dicts: each has 'order' plus either 'filled_ratio' or 'error'.
    """
    results: List[Dict[str, Any]] = []
    for order in orders:
        try:
            res = simulator.create_order(**order)
            ratio = res["filled"] / order.get("amount", 1.0)
            results.append({"order": order, "filled_ratio": ratio})
            logger.info(f"Order {order} filled_ratio={ratio:.2f}")
        except Exception as e:
            results.append({"order": order, "error": str(e)})
            logger.error(f"Order {order} error: {e}")
    return results
