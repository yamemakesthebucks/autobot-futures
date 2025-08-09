from __future__ import annotations
import os
import logging
from typing import Any

from src.execution.exchange_factory import make_exchange

logger = logging.getLogger(__name__)


class PaperTrader:
    """
    Minimal paper-trading runner that pulls OHLCV via ccxt and hands it to the strategy.
    """

    def __init__(self, strategy: Any, cfg: Any):
        self.strategy = strategy
        self.cfg = cfg

        exchange_id = getattr(cfg, "EXCHANGE_ID", os.getenv("EXCHANGE_ID", "binance"))
        market_type = getattr(cfg, "DEFAULT_MARKET_TYPE", os.getenv("DEFAULT_MARKET_TYPE", "spot"))
        symbol = getattr(cfg, "SYMBOL", os.getenv("SYMBOL", "BTC/USDT"))

        api_key = os.getenv("API_KEY")
        api_secret = os.getenv("API_SECRET")

        self.exchange = make_exchange(
            exchange_id,
            api_key=api_key,
            api_secret=api_secret,
            market_type=market_type,
            symbol=symbol,
        )
        self._is_binance_like = exchange_id.lower().startswith("binance")

    def run(self) -> None:
        # For Binance we deliberately skip load_markets; our factory seeded everything
        if not self._is_binance_like:
            try:
                self.exchange.load_markets(reload=False)
            except Exception as e:
                logger.warning("load_markets failed (continuing anyway): %s", e)
        else:
            logger.info("Using seeded Binance markets (no exchangeInfo/currencies calls).")

        ohlcv = self.exchange.fetch_ohlcv(self.cfg.SYMBOL, self.cfg.TIMEFRAME, limit=100)
        logger.info("Fetched %d candles for %s %s", len(ohlcv), self.cfg.SYMBOL, self.cfg.TIMEFRAME)
        # TODO: hand off to your signal/backtest pipeline
