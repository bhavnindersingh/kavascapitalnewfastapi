from kiteconnect import KiteTicker
from typing import Dict, List, Optional, Callable
import json
import asyncio
import logging
from ..schemas.market_data import KiteTick
from ..core.config import get_settings
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebSocketManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        self.settings = get_settings()
        self.kws: Optional[KiteTicker] = None
        self.active_tokens: Dict[int, int] = {}  # token: mode
        self.callbacks: List[Callable] = []
        self.is_connected = False
        self.reconnect_interval = 5  # seconds
        self.max_reconnect_attempts = 5
        self.initialized = True

    async def connect(self, access_token: str):
        """Initialize and connect to Kite WebSocket"""
        try:
            self.kws = KiteTicker(
                api_key=self.settings.KITE_API_KEY,
                access_token=access_token
            )
            
            def on_connect(ws, response):
                self.is_connected = True
                logger.info("Successfully connected to WebSocket")
                if self.active_tokens:
                    self.subscribe(list(self.active_tokens.keys()))

            def on_close(ws, code, reason):
                self.is_connected = False
                logger.warning(f"WebSocket connection closed: {code} - {reason}")
                asyncio.create_task(self.reconnect())

            def on_error(ws, code, reason):
                logger.error(f"WebSocket error: {code} - {reason}")

            def on_message(ws, data: bytes):
                try:
                    ticks = self.kws.parse_binary(data)
                    for tick_data in ticks:
                        tick = KiteTick(
                            **tick_data,
                            timestamp=datetime.utcnow()
                        )
                        for callback in self.callbacks:
                            asyncio.create_task(callback(tick))
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

            self.kws.on_connect = on_connect
            self.kws.on_close = on_close
            self.kws.on_error = on_error
            self.kws.on_message = on_message

            self.kws.connect(threaded=True)
            
        except Exception as e:
            logger.error(f"Error connecting to WebSocket: {e}")
            raise

    async def reconnect(self):
        """Handle WebSocket reconnection"""
        attempts = 0
        while not self.is_connected and attempts < self.max_reconnect_attempts:
            try:
                logger.info(f"Attempting to reconnect... (Attempt {attempts + 1})")
                await self.connect(self.settings.KITE_ACCESS_TOKEN)
                break
            except Exception as e:
                logger.error(f"Reconnection attempt failed: {e}")
                attempts += 1
                await asyncio.sleep(self.reconnect_interval)

    def subscribe(self, tokens: List[int], mode: int = 1):
        """Subscribe to given instrument tokens"""
        if not self.is_connected:
            logger.warning("WebSocket not connected. Storing tokens for later subscription")
            for token in tokens:
                self.active_tokens[token] = mode
            return

        try:
            self.kws.subscribe(tokens)
            self.kws.set_mode(mode, tokens)
            for token in tokens:
                self.active_tokens[token] = mode
            logger.info(f"Subscribed to tokens: {tokens} with mode: {mode}")
        except Exception as e:
            logger.error(f"Error subscribing to tokens: {e}")
            raise

    def unsubscribe(self, tokens: List[int]):
        """Unsubscribe from given instrument tokens"""
        if not self.is_connected:
            logger.warning("WebSocket not connected")
            return

        try:
            self.kws.unsubscribe(tokens)
            for token in tokens:
                self.active_tokens.pop(token, None)
            logger.info(f"Unsubscribed from tokens: {tokens}")
        except Exception as e:
            logger.error(f"Error unsubscribing from tokens: {e}")
            raise

    def add_callback(self, callback: Callable):
        """Add a callback function to handle incoming ticks"""
        self.callbacks.append(callback)
        logger.debug(f"Added callback: {callback.__name__}")

    def remove_callback(self, callback: Callable):
        """Remove a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            logger.debug(f"Removed callback: {callback.__name__}")

    async def close(self):
        """Close the WebSocket connection"""
        if self.kws:
            self.kws.close()
            logger.info("WebSocket connection closed")
