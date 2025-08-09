#!/usr/bin/env python
import os, logging
from dotenv import load_dotenv

from src.utils.config import Config
from src.utils.logger import get_logger
from src.strategy.example_momentum import ExampleMomentumStrategy
from src.backtesting.backtester import Backtester
from src.paper_trading.paper_trader import PaperTrader
from src.deployment.dashboard import launch_dashboard

# near your main entrypoint in main.py, after other imports
import os

if os.getenv("DASHBOARD", "0").lower() in ("1", "true", "yes", "on"):
    try:
        from src.deployment.dashboard import launch_dashboard
        launch_dashboard()
    except Exception as e:
        print(f"[dashboard] skipped: {e}")


def main():
    load_dotenv()
    cfg = Config()
    logger = get_logger("main")
    logger.info("Starting bot in %s mode", cfg.BOT_MODE)

    strategy = ExampleMomentumStrategy(cfg)

    if cfg.BOT_MODE == "backtest":
        # TODO: load historical DataFrame
        df = None
        bt = Backtester(strategy, df, cfg)
        results = bt.run()
        logger.info("Backtest PnL: %s", results)

    elif cfg.BOT_MODE == "paper":
        pt = PaperTrader(strategy, cfg)
        pt.run()

    elif cfg.BOT_MODE == "live":
        # TODO: initialize live trading client
        pass

    launch_dashboard()

if __name__ == "__main__":
    main()


