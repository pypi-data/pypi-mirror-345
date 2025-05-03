from decimal import Decimal
from dataclasses import dataclass

from aiomexc.enums import OrderStatus, OrderType, OrderSide


@dataclass
class Order:
    symbol: str
    order_id: str
    order_list_id: int | None
    client_order_id: str | None
    price: Decimal
    orig_qty: Decimal
    executed_qty: Decimal
    cummulative_quote_qty: Decimal
    status: OrderStatus
    time_in_force: int | None
    type: OrderType
    side: OrderSide
    stop_price: Decimal | None
    time: int
    update_time: int | None
    is_working: bool
    orig_quote_order_qty: Decimal | None
