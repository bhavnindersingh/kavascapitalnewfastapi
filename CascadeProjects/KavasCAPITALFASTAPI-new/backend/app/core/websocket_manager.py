from kiteconnect import KiteTicker
from app.core.config import get_settings
from typing import Dict, Set
from fastapi import WebSocket
import logging
import json
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self._instance = None
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[int]] = {}
        self.kws = None
        self.initialize_ticker()

    def initialize_ticker(self):
        """Initialize KiteTicker"""
        try:
            settings = get_settings()
            self.kws = KiteTicker(
                api_key=settings.KITE_API_KEY,
                access_token=settings.KITE_ACCESS_TOKEN
            )
            self._setup_callbacks()
            self.kws.connect(threaded=True)
            logger.info("KiteTicker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize KiteTicker: {str(e)}")

    def _setup_callbacks(self):
        """Setup KiteTicker callbacks"""
        self.kws.on_ticks = self._on_ticks
        self.kws.on_connect = self._on_connect
        self.kws.on_close = self._on_close
        self.kws.on_error = self._on_error
        self.kws.on_reconnect = self._on_reconnect
        self.kws.on_noreconnect = self._on_noreconnect

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
        """Subscribe to instruments"""
        if client_id in self.subscriptions:
            self.subscriptions[client_id].update(instrument_tokens)
            all_subscriptions = set().union(*self.subscriptions.values())
            if all_subscriptions:
                self.kws.subscribe(list(all_subscriptions))
                logger.info(f"Client {client_id} subscribed to {instrument_tokens}")

    def unsubscribe(self, client_id: str, instrument_tokens: list):
        """Unsubscribe from instruments"""
        if client_id in self.subscriptions:
            self.subscriptions[client_id].difference_update(instrument_tokens)
            all_subscriptions = set().union(*self.subscriptions.values())
            if all_subscriptions:
                self.kws.subscribe(list(all_subscriptions))
            logger.info(f"Client {client_id} unsubscribed from {instrument_tokens}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client {client_id}: {str(e)}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    # KiteTicker callbacks
    def _on_ticks(self, ws, ticks):
        """Handle incoming ticks"""
        for tick in ticks:
            instrument_token = tick.get('instrument_token')
            if instrument_token:
                message = {
                    'type': 'tick',
                    'data': tick,
                    'timestamp': datetime.now().isoformat()
                }
                asyncio.create_task(self.broadcast(message))

    def _on_connect(self, ws, response):
        """Handle connection established"""
        logger.info("Connected to Kite WebSocket")
        all_subscriptions = set().union(*self.subscriptions.values())
        if all_subscriptions:
            self.kws.subscribe(list(all_subscriptions))

    def _on_close(self, ws, code, reason):
        """Handle connection closed"""
        logger.warning(f"Kite WebSocket connection closed: {code} - {reason}")

    def _on_error(self, ws, code, reason):
        """Handle connection error"""
        logger.error(f"Kite WebSocket error: {code} - {reason}")

    def _on_reconnect(self, ws, attempts_count):
        """Handle reconnection attempt"""
        logger.info(f"Attempting to reconnect to Kite WebSocket: attempt {attempts_count}")

    def _on_noreconnect(self, ws):
        """Handle failed reconnection"""
        logger.error("Failed to reconnect to Kite WebSocket")
