from kiteconnect import KiteConnect, KiteTicker
from app.core.config import settings
import logging
import json
from typing import Callable, Dict, List, Optional
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class KiteService:
    _instance = None
    _kite: Optional[KiteConnect] = None
    _ticker: Optional[KiteTicker] = None
    _access_token: Optional[str] = None
    _callbacks: List[Callable] = []
    _subscribed_tokens: Dict[int, bool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KiteService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._kite:
            self._kite = KiteConnect(api_key=settings.KITE_API_KEY)
            logger.info("KiteConnect instance initialized")

    def set_access_token(self, access_token: str):
        """Set the access token for both KiteConnect and KiteTicker"""
        self._access_token = access_token
        self._kite.set_access_token(access_token)
        
        # Initialize ticker with the new access token
        if self._ticker:
            self._ticker.close()
        
        self._ticker = KiteTicker(settings.KITE_API_KEY, access_token)
        self._setup_ticker()
        logger.info("Access token set and ticker initialized")

    def _setup_ticker(self):
        """Set up WebSocket ticker event handlers"""
        if not self._ticker:
            return

        @self._ticker.on_connect
        def on_connect():
            logger.info("Ticker connected")
            # Resubscribe to tokens after reconnection
            if self._subscribed_tokens:
                tokens = list(self._subscribed_tokens.keys())
                self._ticker.subscribe(tokens)
                self._ticker.set_mode(self._ticker.MODE_FULL, tokens)
                logger.info(f"Resubscribed to tokens: {tokens}")

        @self._ticker.on_close
        def on_close():
            logger.info("Ticker connection closed")

        @self._ticker.on_error
        def on_error(error):
            logger.error(f"Ticker error: {error}")

        @self._ticker.on_message
        def on_message(ws, data):
            try:
                # Process the tick data
                if isinstance(data, dict):
                    self._process_tick(data)
                elif isinstance(data, list):
                    for tick in data:
                        self._process_tick(tick)
            except Exception as e:
                logger.error(f"Error processing ticker message: {e}")

        @self._ticker.on_reconnect
        def on_reconnect(reconnect_count, reconnect_interval):
            logger.info(f"Ticker reconnecting: attempt {reconnect_count}, interval {reconnect_interval}s")

        # Start the ticker in a separate thread
        self._ticker.connect(threaded=True)

    def _process_tick(self, tick: Dict):
        """Process individual tick data"""
        try:
            # Convert Kite tick format to our format
            processed_data = {
                "type": "MARKET_DATA",
                "data": {
                    "instrument_token": tick.get("instrument_token"),
                    "last_price": tick.get("last_price"),
                    "volume": tick.get("volume"),
                    "oi": tick.get("oi", 0),
                    "change": tick.get("change", 0),
                    "timestamp": datetime.fromtimestamp(tick.get("timestamp", 0)).isoformat()
                }
            }

            # Notify all callbacks
            for callback in self._callbacks:
                asyncio.create_task(callback(processed_data))

        except Exception as e:
            logger.error(f"Error processing tick: {e}")

    def subscribe(self, tokens: List[int]):
        """Subscribe to market data for given instrument tokens"""
        try:
            if not self._ticker or not tokens:
                return

            # Update subscribed tokens
            for token in tokens:
                self._subscribed_tokens[token] = True

            # Subscribe and set mode to full
            self._ticker.subscribe(tokens)
            self._ticker.set_mode(self._ticker.MODE_FULL, tokens)
            logger.info(f"Subscribed to tokens: {tokens}")

        except Exception as e:
            logger.error(f"Error subscribing to tokens: {e}")
            raise

    def unsubscribe(self, tokens: List[int]):
        """Unsubscribe from market data for given instrument tokens"""
        try:
            if not self._ticker or not tokens:
                return

            # Remove from subscribed tokens
            for token in tokens:
                self._subscribed_tokens.pop(token, None)

            self._ticker.unsubscribe(tokens)
            logger.info(f"Unsubscribed from tokens: {tokens}")

        except Exception as e:
            logger.error(f"Error unsubscribing from tokens: {e}")
            raise

    def add_market_data_callback(self, callback: Callable):
        """Add a callback for market data updates"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def remove_market_data_callback(self, callback: Callable):
        """Remove a callback for market data updates"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    async def get_instruments(self, exchange: str = None) -> List[Dict]:
        """Get list of instruments from Kite"""
        try:
            if not self._kite:
                raise Exception("KiteConnect not initialized")
            
            # Run the synchronous instruments call in a thread pool
            loop = asyncio.get_event_loop()
            instruments = await loop.run_in_executor(None, self._kite.instruments, exchange)
            
            return instruments
        except Exception as e:
            logger.error(f"Error fetching instruments: {e}")
            raise

    async def get_option_chain(self, symbol: str, expiry: str):
        """Get option chain data for a symbol and expiry"""
        try:
            # Get instrument tokens for the options
            instruments = await self._get_option_instruments(symbol, expiry)
            
            # Format the response
            return {
                "stockInfo": {
                    "symbol": symbol,
                    "ltp": 0,  # Will be updated via WebSocket
                    "change": 0,
                    "volume": 0,
                    "oi": 0
                },
                "strikes": instruments
            }

        except Exception as e:
            logger.error(f"Error fetching option chain: {e}")
            raise

    async def _get_option_instruments(self, symbol: str, expiry: str):
        """Get option instruments for a symbol and expiry"""
        try:
            # Get all instruments asynchronously
            loop = asyncio.get_event_loop()
            instruments = await loop.run_in_executor(None, self._kite.instruments)
            
            # Filter options for the given symbol and expiry
            options = []
            for inst in instruments:
                if (inst["name"] == symbol and 
                    inst["instrument_type"] in ["CE", "PE"] and 
                    inst["expiry"].strftime("%Y-%m-%d") == expiry):
                    
                    strike = inst["strike"]
                    instrument_token = inst["instrument_token"]
                    option_type = inst["instrument_type"]
                    
                    # Find or create strike price entry
                    strike_entry = next(
                        (item for item in options if item["strike"] == strike),
                        None
                    )
                    
                    if not strike_entry:
                        strike_entry = {
                            "strike": strike,
                            "call": None,
                            "put": None
                        }
                        options.append(strike_entry)
                    
                    # Add option data
                    option_data = {
                        "strike": strike,
                        "instrument_token": instrument_token,
                        "ltp": 0,  # Will be updated via WebSocket
                        "change": 0,
                        "volume": 0,
                        "oi": 0,
                        "expiry": expiry
                    }
                    
                    if option_type == "CE":
                        strike_entry["call"] = option_data
                    else:
                        strike_entry["put"] = option_data

            # Sort by strike price
            options.sort(key=lambda x: x["strike"])
            return options

        except Exception as e:
            logger.error(f"Error getting option instruments: {e}")
            raise
