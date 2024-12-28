from pydantic import BaseModel
from typing import List, Optional

class TokenResponse(BaseModel):
    access_token: str
    
class MarketDepth(BaseModel):
    buy_quantity: int
    sell_quantity: int
    buy_price: float
    sell_price: float

class KiteQuote(BaseModel):
    instrument_token: int
    last_price: float
    volume: int
    buy_quantity: int
    sell_quantity: int
    oi: Optional[int]
    timestamp: str

class WebSocketRequest(BaseModel):
    type: str  # 'subscribe' or 'unsubscribe'
    tokens: List[int]

class WebSocketResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict]
