from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Union
from decimal import Decimal

class OHLC(BaseModel):
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

class DepthItem(BaseModel):
    price: Decimal
    quantity: int
    orders: int

class MarketDepth(BaseModel):
    buy: List[DepthItem]
    sell: List[DepthItem]

class KiteTick(BaseModel):
    tradeable: bool
    mode: int = Field(..., description="1: LTP, 2: Quote, 3: Full")
    instrument_token: int
    last_price: Decimal
    last_quantity: Optional[int] = None
    average_price: Optional[Decimal] = None
    volume: Optional[int] = None
    buy_quantity: Optional[int] = None
    sell_quantity: Optional[int] = None
    ohlc: Optional[OHLC] = None
    depth: Optional[MarketDepth] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class InstrumentType(BaseModel):
    instrument_token: int
    exchange_token: int
    tradingsymbol: str
    name: Optional[str] = None
    last_price: Decimal
    expiry: Optional[datetime] = None
    strike: Optional[Decimal] = None
    tick_size: Decimal
    lot_size: int
    instrument_type: str  # EQ, FUT, CE, PE, etc.
    segment: str
    exchange: str

class OptionInstrument(InstrumentType):
    underlying: str
    option_type: str  # CE or PE
    strike: Decimal
    expiry: datetime

class FutureInstrument(InstrumentType):
    underlying: str
    expiry: datetime

class WebSocketSubscription(BaseModel):
    tokens: List[int]
    mode: int = Field(..., description="1: LTP, 2: Quote, 3: Full")
