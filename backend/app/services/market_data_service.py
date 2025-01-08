from typing import Dict, List, Optional, Set, Callable
from datetime import datetime, timedelta
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.market_data import KiteTick, MarketDepth, OHLC
from app.repositories.market_data import MarketDataRepository
from app.repositories.instruments import InstrumentRepository
from app.services.websocket_manager import WebSocketManager
import redis
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class MarketDataService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketDataService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        self.settings = get_settings()
        self.ws_manager = WebSocketManager()
        self.active_subscriptions: Dict[int, int] = {}  # token: mode
        self.tick_callbacks: List[Callable] = []
        self.depth_callbacks: List[Callable] = []
        self.ohlc_intervals = ["1min", "5min", "15min", "60min", "1day"]
        self.last_ohlc_update: Dict[str, datetime] = {}
        
        # Initialize Redis connection
        self.redis = redis.from_url(self.settings.REDIS_URL, decode_responses=True)
        
        self.initialized = True

    async def start(self, session: AsyncSession):
        """Initialize the market data service."""
        self.market_data_repo = MarketDataRepository(session)
        self.instrument_repo = InstrumentRepository(session)
        
        # Register WebSocket callbacks
        self.ws_manager.add_callback(self._process_tick)
        
        # Start OHLCV calculation task
        asyncio.create_task(self._calculate_ohlcv_periodic())

    async def _process_tick(self, tick: KiteTick):
        """Process incoming tick data."""
        try:
            # Store tick in Redis for real-time access
            await self._update_redis_tick(tick)
            
            # Store tick in database
            tick_dict = tick.dict()
            await self.market_data_repo.add_tick(tick_dict)
            
            # Process market depth if available
            if tick.depth:
                await self._process_market_depth(tick.instrument_token, tick.depth, tick.timestamp)
            
            # Notify callbacks
            for callback in self.tick_callbacks:
                try:
                    await callback(tick)
                except Exception as e:
                    logger.error(f"Error in tick callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing tick: {e}")

    async def _process_market_depth(self, instrument_token: int, depth: MarketDepth, timestamp: datetime):
        """Process market depth data."""
        try:
            # Store depth in Redis
            depth_key = f"depth:{instrument_token}"
            await self._update_redis_depth(depth_key, depth)
            
            # Store in database
            depth_dict = {
                "instrument_token": instrument_token,
                "timestamp": timestamp,
                "depth_buy": [level.dict() for level in depth.buy],
                "depth_sell": [level.dict() for level in depth.sell]
            }
            await self.market_data_repo.add_market_depth(depth_dict)
            
            # Notify callbacks
            for callback in self.depth_callbacks:
                try:
                    await callback(instrument_token, depth)
                except Exception as e:
                    logger.error(f"Error in depth callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing market depth: {e}")

    async def _update_redis_tick(self, tick: KiteTick):
        """Update tick data in Redis."""
        try:
            tick_key = f"tick:{tick.instrument_token}"
            tick_data = tick.dict()
            self.redis.hset(tick_key, mapping=tick_data)
            self.redis.expire(tick_key, 300)  # Expire after 5 minutes
        except Exception as e:
            logger.error(f"Error updating Redis tick: {e}")

    async def _update_redis_depth(self, key: str, depth: MarketDepth):
        """Update market depth in Redis."""
        try:
            depth_data = depth.dict()
            self.redis.hset(key, mapping=depth_data)
            self.redis.expire(key, 300)  # Expire after 5 minutes
        except Exception as e:
            logger.error(f"Error updating Redis depth: {e}")

    async def _calculate_ohlcv_periodic(self):
        """Periodically calculate OHLCV data."""
        while True:
            try:
                current_time = datetime.utcnow()
                
                for interval in self.ohlc_intervals:
                    last_update = self.last_ohlc_update.get(interval, datetime.min)
                    interval_seconds = {
                        "1min": 60,
                        "5min": 300,
                        "15min": 900,
                        "60min": 3600,
                        "1day": 86400
                    }[interval]
                    
                    if (current_time - last_update).total_seconds() >= interval_seconds:
                        # Calculate OHLCV for all active instruments
                        instruments = await self.instrument_repo.get_active_instruments()
                        for instrument in instruments:
                            await self.market_data_repo.calculate_ohlcv(
                                instrument.instrument_token,
                                interval,
                                last_update,
                                current_time
                            )
                        self.last_ohlc_update[interval] = current_time
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error calculating OHLCV: {e}")
                await asyncio.sleep(60)  # Retry after a minute

    async def subscribe_instruments(self, tokens: List[int], mode: int = 1):
        """Subscribe to market data for instruments."""
        try:
            # Update subscription mode for tokens
            for token in tokens:
                self.active_subscriptions[token] = mode
            
            # Subscribe via WebSocket
            await self.ws_manager.subscribe(tokens, mode)
            
            logger.info(f"Subscribed to instruments: {tokens} with mode {mode}")
            
        except Exception as e:
            logger.error(f"Error subscribing to instruments: {e}")
            raise

    async def unsubscribe_instruments(self, tokens: List[int]):
        """Unsubscribe from market data for instruments."""
        try:
            # Remove from active subscriptions
            for token in tokens:
                self.active_subscriptions.pop(token, None)
            
            # Unsubscribe via WebSocket
            await self.ws_manager.unsubscribe(tokens)
            
            logger.info(f"Unsubscribed from instruments: {tokens}")
            
        except Exception as e:
            logger.error(f"Error unsubscribing from instruments: {e}")
            raise

    def add_tick_callback(self, callback: Callable):
        """Add callback for tick data."""
        self.tick_callbacks.append(callback)

    def add_depth_callback(self, callback: Callable):
        """Add callback for market depth data."""
        self.depth_callbacks.append(callback)

    async def get_latest_tick(self, instrument_token: int) -> Optional[KiteTick]:
        """Get latest tick data for an instrument."""
        try:
            # Try Redis first
            tick_key = f"tick:{instrument_token}"
            tick_data = self.redis.hgetall(tick_key)
            
            if tick_data:
                return KiteTick(**tick_data)
            
            # Fall back to database
            return await self.market_data_repo.get_latest_tick(instrument_token)
            
        except Exception as e:
            logger.error(f"Error getting latest tick: {e}")
            return None

    async def get_latest_depth(self, instrument_token: int) -> Optional[MarketDepth]:
        """Get latest market depth for an instrument."""
        try:
            # Try Redis first
            depth_key = f"depth:{instrument_token}"
            depth_data = self.redis.hgetall(depth_key)
            
            if depth_data:
                return MarketDepth(**depth_data)
            
            # Fall back to database
            return await self.market_data_repo.get_latest_depth(instrument_token)
            
        except Exception as e:
            logger.error(f"Error getting latest depth: {e}")
            return None
