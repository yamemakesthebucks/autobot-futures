"""
Optuna-based parameter optimization for momentum strategies.
"""

import json
from pathlib import Path
from typing import Dict

import optuna
import pandas as pd

from src.strategy.example_momentum import ExampleMomentumStrategy
from src.backtesting.backtester import Backtester


def objective(trial: optuna.Trial, df: pd.DataFrame) -> float:
    """
    Objective function for Optuna: maximize backtest PnL.
    Tunes EMA spans.
    """
    # Prepare DataFrame with timestamp index
    df_copy = df.copy()
    df_copy["timestamp"] = pd.to_datetime(df_copy["timestamp"])
    df_copy.set_index("timestamp", inplace=True)

    span_short = trial.suggest_int("span_short", 2, 10)
    span_long = trial.suggest_int("span_long", span_short + 1, 20)
    size = trial.suggest_float("size", 0.1, 1.0)

    strat = ExampleMomentumStrategy(size=size, span_short=span_short, span_long=span_long)
    bt = Backtester(strat, df_copy, None)
    result = bt.run()
    # If no 'pnl' key or empty, return 0.0
    return result.get("pnl", 0.0)


def run_optimization(
    df: pd.DataFrame,
    n_trials: int = 20,
    storage_path: str = "optuna_study.json"
) -> Dict:
    """
    Run Optuna study and save best parameters.

    Args:
        df: Historical OHLCV DataFrame.
        n_trials: Number of trials to run.
        storage_path: JSON file to write best params.

    Returns:
        The best parameters dict.
    """
    study = optuna.create_study(direction="maximize")
    study.optimize(lambda t: objective(t, df), n_trials=n_trials)

    best: Dict = study.best_params
    # Save to JSON
    Path(storage_path).write_text(json.dumps(best, indent=2))
    return best


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", help="Path to CSV with OHLCV data")
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--output", default="optuna_study.json")
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv, parse_dates=["timestamp"])
    best = run_optimization(df, n_trials=args.trials, storage_path=args.output)
    print("Best parameters:", best)
