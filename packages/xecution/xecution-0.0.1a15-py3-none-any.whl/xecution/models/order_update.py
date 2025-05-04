from dataclasses import dataclass
from datetime import datetime
from xecution.common.enums import Exchange, OrderSide, OrderStatus, OrderType, Symbol, TimeInForce

@dataclass
class OrderUpdate:
    symbol: Symbol
    order_type: OrderType
    side: OrderSide
    time_in_force: TimeInForce
    exchange_order_id: str
    order_time: datetime
    updated_time: datetime
    size: float
    filled_size: float
    remain_size: float
    price: float
    client_order_id: str
    status: OrderStatus
    exchange: Exchange = Exchange.Binance
    is_reduce_only: bool = False
    is_hedge_mode: bool = False

@dataclass
class OrderResponse:
    exchange_order_id: str
    client_order_id: str