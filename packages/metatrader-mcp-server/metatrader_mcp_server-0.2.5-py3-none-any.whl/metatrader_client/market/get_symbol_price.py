from typing import Dict, Any
from datetime import datetime, timezone
import MetaTrader5 as mt5
from ..exceptions import SymbolNotFoundError, MarketDataError

def get_symbol_price(connection, symbol_name: str) -> Dict[str, Any]:
    tick = mt5.symbol_info_tick(symbol_name)
    if tick is None:
        raise SymbolNotFoundError(f"Could not get price data for symbol '{symbol_name}'")
    tick_time = datetime.fromtimestamp(tick.time, tz=timezone.utc)
    return {
        "bid": tick.bid,
        "ask": tick.ask,
        "last": tick.last,
        "volume": tick.volume,
        "time": tick_time
    }
