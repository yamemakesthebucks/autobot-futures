"""
Stress testing: Monte Carlo simulations and black-swan shocks.
"""

import logging
from typing import Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def monte_carlo_returns(
    returns: pd.Series,
    n_sims: int,
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Generate Monte Carlo return simulations by sampling with replacement.

    Args:
        returns: Series of historical period returns (e.g. 0.01 for +1%).
        n_sims: Number of simulated trajectories.
        seed: Optional RNG seed for reproducibility.

    Returns:
        DataFrame of shape (len(returns), n_sims) where each column is one sim.
    """
    rng = np.random.default_rng(seed)
    sims = rng.choice(returns.values, size=(len(returns), n_sims), replace=True)
    sim_df = pd.DataFrame(sims, index=returns.index)
    logger.info(f"Generated {n_sims} Monte Carlo simulations")
    return sim_df


def simulate_pnl(
    sim_returns: pd.DataFrame,
    initial_capital: float
) -> pd.Series:
    """
    Compute final PnL for each Monte Carlo simulation.

    Args:
        sim_returns: DataFrame from monte_carlo_returns().
        initial_capital: Starting capital.

    Returns:
        Series of final capital values, indexed by simulation column.
    """
    # Compute cumulative growth per sim
    cumulative = (1 + sim_returns).cumprod(axis=0) * initial_capital
    finals = cumulative.iloc[-1]
    logger.info("Computed final PnL for all simulations")
    return finals


def inject_black_swan(
    returns: pd.Series,
    shock_pct: float,
    on_index: pd.Timestamp
) -> pd.Series:
    """
    Inject a one-time shock into returns at the specified timestamp.

    Args:
        returns: Series of historical returns.
        shock_pct: One-off return shock (e.g. -0.5 for -50%).
        on_index: The timestamp at which to apply the shock.

    Returns:
        A new Series with the shock applied.

    Raises:
        KeyError: If `on_index` not in `returns.index`.
    """
    if on_index not in returns.index:
        raise KeyError(f"Shock timestamp {on_index} not in index")
    shocked = returns.copy()
    shocked.loc[on_index] += shock_pct
    logger.info(f"Injected black-swan shock of {shock_pct} at {on_index}")
    return shocked
