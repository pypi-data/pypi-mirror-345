import json
import uuid

from .enums import OrderType, Side


class OrderSingle:
    """
    Represents a basic single-leg order (equity or option).
    """

    def __init__(
        self,
        symbol: str,
        side: Side,
        order_qty: int,
        order_type: OrderType,
        price: float = None,
    ):
        if not symbol:
            raise ValueError("Symbol cannot be empty")
        if not isinstance(side, Side):
            raise ValueError("Side must be a valid Side enum value")
        if not isinstance(order_type, OrderType):
            raise ValueError("OrderType must be a valid OrderType enum value")
        if order_qty <= 0:
            raise ValueError("OrderQty must be positive")
        if order_type == OrderType.LIMIT and (price is None or price <= 0):
            raise ValueError("Limit orders must have a positive price")

        self.client_order_id = str(uuid.uuid4())
        self.symbol = symbol
        self.side = side
        self.order_qty = order_qty
        self.order_type = order_type
        self.price = price

    def to_dict(self):
        order = {
            "MsgType": "D",  # OrderSingle
            "ClientOrderID": self.client_order_id,
            "Symbol": self.symbol,
            "Side": self.side.value,
            "OrderQty": self.order_qty,
            "OrderType": self.order_type.value,
        }
        if self.price is not None:
            # Lightspeed API expects price as a string
            order["Price"] = str(self.price)
        return order

    def to_json(self):
        return json.dumps(self.to_dict())
