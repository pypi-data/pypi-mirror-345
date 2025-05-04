from dataclasses import dataclass
from typing import List


@dataclass
class Level:
    price: float
    quantity: float

@dataclass 
class OrderBookSnapshot:
    bids: List[Level]
    asks: List[Level]