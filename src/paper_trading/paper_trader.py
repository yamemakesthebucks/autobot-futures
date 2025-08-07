import ccxt, time
from src.utils.logger import get_logger

class PaperTrader:
    def __init__(self, strategy, cfg):
        self.strategy = strategy
        self.cfg = cfg
        self.logger = get_logger("PaperTrader")
        self.exchange = ccxt.binance({
            "apiKey": cfg.API_KEY,
            "secret": cfg.API_SECRET,
            "enableRateLimit": True,
            "options": {"defaultType":"future"},
            "urls": {"api": {"public":"https://testnet.binancefuture.com/fapi/v1",
                             "private":"https://testnet.binancefuture.com/fapi/v1"}}
        })

    def run(self):
        # fetch recent candle, generate signals, place orders
        ohlcv = self.exchange.fetch_ohlcv(self.cfg.SYMBOL, self.cfg.TIMEFRAME, limit=100)
        import pandas as pd
        df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
        signals = self.strategy.generate_signals(df)
        for sig in signals:
            order = self.exchange.create_order(
                symbol=self.cfg.SYMBOL, type="MARKET",
                side=sig["side"].upper(), amount=sig["size"]
            )
            self.logger.info("Placed %s order @ %s", sig["side"], order["price"])
            time.sleep(1)
