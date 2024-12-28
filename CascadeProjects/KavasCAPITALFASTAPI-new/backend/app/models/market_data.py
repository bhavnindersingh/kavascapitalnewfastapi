from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, Enum, Boolean, JSON, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base_class import Base

class InstrumentType(str, enum.Enum):
    EQUITY = "EQ"
    FUTURE = "FUT"
    CALL_OPTION = "CE"
    PUT_OPTION = "PE"
    INDEX = "IDX"

class Instrument(Base):
    __tablename__ = "instruments"

    instrument_token = Column(Integer, primary_key=True)
    exchange_token = Column(Integer, nullable=False)
    tradingsymbol = Column(String(50), nullable=False)
    name = Column(String(100))
    last_price = Column(Float)
    expiry = Column(DateTime(timezone=True))
    strike = Column(Float)
    tick_size = Column(Float)
    lot_size = Column(Integer)
    instrument_type = Column(String(10), nullable=False)
    segment = Column(String(20), nullable=False)
    exchange = Column(String(10), nullable=False)
    underlying = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)

    __table_args__ = (
        Index('instruments_tradingsymbol_exchange_key', 'tradingsymbol', 'exchange', unique=True),
    )

class TickData(Base):
    __tablename__ = "tick_data"

    instrument_token = Column(Integer, ForeignKey("instruments.instrument_token"), primary_key=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    last_price = Column(Float, nullable=False)
    last_quantity = Column(Integer)
    average_price = Column(Float)
    volume = Column(Integer)
    buy_quantity = Column(Integer)
    sell_quantity = Column(Integer)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    change = Column(Float)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    
    instrument = relationship("Instrument")

    __table_args__ = (
        Index('tick_data_instrument_token_timestamp_idx', 'instrument_token', 'timestamp', unique=True),
    )

class MarketDepth(Base):
    __tablename__ = "market_depth"
    
    instrument_token = Column(Integer, ForeignKey("instruments.instrument_token"), primary_key=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    depth_buy = Column(JSONB)
    depth_sell = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    
    instrument = relationship("Instrument")

    __table_args__ = (
        Index('market_depth_instrument_token_timestamp_idx', 'instrument_token', 'timestamp', unique=True),
    )

class OHLCV(Base):
    __tablename__ = "ohlcv"
    
    instrument_token = Column(Integer, ForeignKey("instruments.instrument_token"), primary_key=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    interval = Column(String(20), primary_key=True, nullable=False)  
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    
    instrument = relationship("Instrument")

    __table_args__ = (
        Index('ohlcv_instrument_token_interval_timestamp_idx', 'instrument_token', 'interval', 'timestamp', unique=True),
    )

class OptionsChain(Base):
    __tablename__ = "options_chain"
    
    instrument_token = Column(Integer, ForeignKey("instruments.instrument_token"), primary_key=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    underlying = Column(String(50), primary_key=True, nullable=False)
    expiry = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    strike = Column(Float, primary_key=True, nullable=False)
    option_type = Column(String(2), primary_key=True, nullable=False)
    last_price = Column(Float)
    volume = Column(Integer)
    oi = Column(Integer)
    oi_change = Column(Integer)
    iv = Column(Float)
    delta = Column(Float)
    theta = Column(Float)
    gamma = Column(Float)
    vega = Column(Float)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    
    instrument = relationship("Instrument")

    __table_args__ = (
        Index('options_chain_underlying_expiry_strike_option_type_timestamp_idx', 
              'underlying', 'expiry', 'strike', 'option_type', 'timestamp', unique=True),
    )
