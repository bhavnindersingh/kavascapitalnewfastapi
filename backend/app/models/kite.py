from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    instrument_token = Column(Integer, unique=True, index=True)
    trading_symbol = Column(String, index=True)
    name = Column(String)
    expiry = Column(DateTime, nullable=True)
    strike = Column(Float, nullable=True)
    tick_size = Column(Float)
    lot_size = Column(Integer)
    instrument_type = Column(String)
    segment = Column(String)
    exchange = Column(String)

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    instrument_token = Column(Integer, ForeignKey("instruments.instrument_token"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    last_price = Column(Float)
    volume = Column(Integer)
    buy_quantity = Column(Integer)
    sell_quantity = Column(Integer)
    oi = Column(Integer, nullable=True)
    
    instrument = relationship("Instrument")
