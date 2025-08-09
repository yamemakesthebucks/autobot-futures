from __future__ import annotations
from typing import Optional, Dict, Any
import types
import ccxt


def _binance_timeframes() -> Dict[str, str]:
    # ccxt expects these for fetch_ohlcv timeframe -> interval
    return {
        "1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "2h": "2h", "4h": "4h", "6h": "6h", "8h": "8h", "12h": "12h",
        "1d": "1d", "3d": "3d", "1w": "1w", "1M": "1M",
    }


def _seed_minimal_market(ex: Any, symbol: str, market_type: str = "spot") -> None:
    """
    Preload a complete-enough markets structure so ccxt/binance can call public Klines
    without ever hitting exchangeInfo or currencies endpoints.
    """
    if not symbol or "/" not in symbol:
        return

    base, quote = symbol.split("/")
    market_id = base + quote  # e.g. BTC/USDT -> BTCUSDT
    is_spot = (market_type == "spot")

    m = {
        "id": market_id,
        "symbol": symbol,
        "base": base,
        "quote": quote,
        "type": market_type,
        "spot": is_spot,
        "future": False,
        "swap": False,
        "margin": False,
        "option": False,
        "contract": False,
        "linear": None,
        "inverse": None,
        "expiry": None,
        "settle": None,
        "active": True,
        "precision": {"price": 8, "amount": 8},
        "limits": {
            "amount": {"min": 1e-8, "max": None},
            "price": {"min": 1e-8, "max": None},
            "cost": {"min": 0.0, "max": None},
        },
        # not strictly required but harmless
        "info": {},
    }

    # Minimal markets/indexes
    ex.markets = {symbol: m}
    ex.markets_by_id = {market_id: m}
    ex.symbols = [symbol]
    ex.ids = [market_id]

    # Timeframes used by fetch_ohlcv
    ex.timeframes = _binance_timeframes()

    # Ensure has[] won’t trigger paths that fetch currencies/markets
    ex.has = dict(getattr(ex, "has", {}))
    ex.has.update({
        "fetchCurrencies": False,
        "fetchMarkets": True,     # we stub it below
        "loadMarkets": True,      # we stub it below
        "fetchOHLCV": True,
    })

    # Bound no-op methods to *instance* so internal calls hit these
    def _no_fetch_currencies(self, *args, **kwargs):
        return {}

    def _no_fetch_markets(self, params: Dict[str, Any] | None = None):
        return [m]

    def _no_load_markets(self, reload: bool = False, params: Dict[str, Any] | None = None):
        return self.markets

    def _market(self, s: str):
        return self.markets[s]

    ex.fetch_currencies = types.MethodType(_no_fetch_currencies, ex)  # type: ignore[attr-defined]
    ex.fetch_markets = types.MethodType(_no_fetch_markets, ex)        # type: ignore[attr-defined]
    ex.load_markets = types.MethodType(_no_load_markets, ex)          # type: ignore[attr-defined]
    ex.market = types.MethodType(_market, ex)                          # helps some ccxt paths


def make_exchange(
    exchange_id: str,
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    market_type: str = "spot",
    symbol: Optional[str] = None,
):
    """
    Build a ccxt exchange instance with safe options that avoid geo-blocked Binance endpoints.
    For Binance* we:
      - Disable fetchCurrencies()
      - Seed a minimal market for `symbol`
      - Override load_markets/fetch_markets/fetch_currencies to no-ops
    """
    exchange_cls = getattr(ccxt, exchange_id)
    ex = exchange_cls(
        {
            "enableRateLimit": True,
            "options": {
                "defaultType": market_type,
                "fetchCurrencies": False,  # don't touch SAPI
            },
        }
    )

    if api_key and api_secret:
        ex.apiKey = api_key
        ex.secret = api_secret

    if exchange_id.lower().startswith("binance"):
        ex.options["fetchCurrencies"] = False
        if symbol:
            _seed_minimal_market(ex, symbol, market_type)

    return ex
