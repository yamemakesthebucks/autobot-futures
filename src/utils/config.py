import os

class Config:
    EXCHANGE_ID    = os.getenv("EXCHANGE_ID", "binance")
    SYMBOL         = os.getenv("SYMBOL", "BTC/USDT")
    TIMEFRAME      = os.getenv("TIMEFRAME", "1m")
    BOT_MODE       = os.getenv("BOT_MODE", "paper")
    MAX_RISK       = float(os.getenv("MAX_RISK_PER_TRADE", "0.01"))
    API_KEY        = os.getenv("API_KEY")
    API_SECRET     = os.getenv("API_SECRET")
