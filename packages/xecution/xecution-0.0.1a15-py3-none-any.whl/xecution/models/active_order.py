from dataclasses import dataclass
from xecution.common.enums import Exchange, Symbol
from xecution.models.position import Position

@dataclass
class ActiveOrder:
    symbol: Symbol
    exchange: Exchange
    updated_time: int
    created_time: int
    exchange_order_id: str
    client_order_id: str
    position: Position