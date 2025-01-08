from kiteconnect import KiteTicker
from config.kite_config import get_kite_settings
import logging
import json
from typing import Dict, Set, Callable
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.settings = get_kite_settings()
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[int]] = {}  # client_id -> set of instrument tokens
        self.kws = None
        self.initialize_ticker()

    def initialize_ticker(self):
        """Initialize KiteTicker"""
        try:
            self.kws = KiteTicker(
                api_key=self.settings.api_key,
                access_token=self.settings.access_token
            )
            self.setup_ticker_callbacks()
            self.kws.connect(threaded=True)
            logger.info("KiteTicker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize KiteTicker: {str(e)}")

    def setup_ticker_callbacks(self):
        """Setup callbacks for the ticker"""
        self.kws.on_ticks = self.on_ticks
        self.kws.on_connect = self.on_connect
        self.kws.on_close = self.on_close
        self.kws.on_error = self.on_error
        self.kws.on_reconnect = self.on_reconnect
        self.kws.on_noreconnect = self.on_noreconnect

    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new client"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        """Disconnect a client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.subscriptions:
            self.unsubscribe(client_id, list(self.subscriptions[client_id]))
            del self.subscriptions[client_id]
        logger.info(f"Client {client_id} disconnected")

    def subscribe(self, client_id: str, instrument_tokens: list):
        """Subscribe to instruments for a client"""
        if client_id in self.subscriptions:
            self.subscriptions[client_id].update(instrument_tokens)
            all_subscriptions = set().union(*self.subscriptions.values())
            self.kws.subscribe(list(all_subscriptions))
            logger.info(f"Client {client_id} subscribed to {instrument_tokens}")

    def unsubscribe(self, client_id: str, instrument_tokens: list):
        """Unsubscribe from instruments for a client"""
        if client_id in self.subscriptions:
            self.subscriptions[client_id].difference_update(instrument_tokens)
            all_subscriptions = set().union(*self.subscriptions.values())
            self.kws.subscribe(list(all_subscriptions))
            logger.info(f"Client {client_id} unsubscribed from {instrument_tokens}")

    async def broadcast_to_subscribers(self, instrument_token: int, data: dict):
        """Broadcast data to all subscribers of an instrument"""
        for client_id, subscribed_tokens in self.subscriptions.items():
            if instrument_token in subscribed_tokens:
                try:
                    websocket = self.active_connections.get(client_id)
                    if websocket:
                        await websocket.send_text(json.dumps(data))
                except Exception as e:
                    logger.error(f"Error broadcasting to client {client_id}: {str(e)}")

    # Ticker callbacks
    def on_ticks(self, ws, ticks):
        """Callback when ticks are received"""
        for tick in ticks:
            instrument_token = tick.get('instrument_token')
            if instrument_token:
                for client_id, websocket in self.active_connections.items():
                    if instrument_token in self.subscriptions.get(client_id, set()):
                        try:
                            websocket.send_text(json.dumps(tick))
                        except Exception as e:
                            logger.error(f"Error sending tick to client {client_id}: {str(e)}")

    def on_connect(self, ws, response):
        """Callback when connection is established"""
        logger.info("Successfully connected to Kite WebSocket")

    def on_close(self, ws, code, reason):
        """Callback when connection is closed"""
        logger.warning(f"Connection closed: {code} - {reason}")

    def on_error(self, ws, code, reason):
        """Callback when error occurs"""
        logger.error(f"Error in WebSocket: {code} - {reason}")

    def on_reconnect(self, ws, attempts_count):
        """Callback when reconnecting"""
        logger.info(f"Reconnecting... {attempts_count} attempts")

    def on_noreconnect(self, ws):
        """Callback when reconnection fails"""
        logger.error("Failed to reconnect to Kite WebSocket")
