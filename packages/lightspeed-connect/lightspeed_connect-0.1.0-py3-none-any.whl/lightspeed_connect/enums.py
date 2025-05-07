from enum import Enum


class Side(str, Enum):
    BUY = "1"
    SELL = "2"
    SELL_SHORT = "5"


class OrderType(str, Enum):
    MARKET = "1"
    LIMIT = "2"
    STOP = "3"
    STOP_LIMIT = "4"
    MARKET_ON_CLOSE = "5"
    LIMIT_ON_CLOSE = "B"
