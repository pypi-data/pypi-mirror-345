from enum import StrEnum
from crypticorn.common.mixins import ValidateEnumMixin, ExcludeEnumMixin


class Exchange(ValidateEnumMixin, ExcludeEnumMixin, StrEnum):
    """Supported exchanges for trading"""

    KUCOIN = "kucoin"
    BINGX = "bingx"


class InternalExchange(ValidateEnumMixin, ExcludeEnumMixin, StrEnum):
    """All exchanges we are using, including public (Exchange)"""

    KUCOIN = "kucoin"
    BINGX = "bingx"
    BINANCE = "binance"
    BYBIT = "bybit"
    HYPERLIQUID = "hyperliquid"
    BITGET = "bitget"


class MarketType(ValidateEnumMixin, ExcludeEnumMixin, StrEnum):
    """
    Market types
    """

    SPOT = "spot"
    FUTURES = "futures"
