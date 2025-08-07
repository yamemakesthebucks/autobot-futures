import pandas as pd

class Backtester:
    def __init__(self, strategy, df: pd.DataFrame, cfg):
        self.strategy = strategy
        self.df = df
        self.cfg = cfg
        self.pnl = 0.0

    def run(self):
        trades = []
        signals = self.strategy.generate_signals(self.df)
        for sig in signals:
            price = self.df.loc[sig["timestamp"], "close"]
            size  = sig["size"]
            if sig["side"] == "buy":
                self.pnl -= price * size
            else:
                self.pnl += price * size
            trades.append(sig)
        return {"pnl": self.pnl, "trades": len(trades)}
