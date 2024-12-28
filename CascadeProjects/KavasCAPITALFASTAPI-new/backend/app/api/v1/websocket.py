from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from starlette.websockets import WebSocketState
from app.services.kite_service import KiteService
from app.core.redis import get_redis
from typing import Dict, Any, Optional
import json
import logging
import asyncio
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.kite_service = KiteService()

    async def connect(self, websocket: WebSocket, client_id: str, token: str):
        """Connect a client and initialize their session"""
        try:
            # Verify token from Redis
            redis = await get_redis()
            stored_token = await redis.get(f"access_token:{token}")
            
            if not stored_token:
                logger.error(f"Invalid token for client {client_id}")
                raise HTTPException(
                    status_code=403,
                    detail="Invalid or expired token"
                )
            
            # Set up Kite connection with the stored token
            self.kite_service.set_access_token(stored_token)
            
            # Accept WebSocket connection
            await websocket.accept()
            self.active_connections[client_id] = websocket
            logger.info(f"Client {client_id} connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect client {client_id}: {str(e)}")
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.close(code=4000, reason=str(e))
            raise

    async def disconnect(self, client_id: str):
        """Disconnect a client and clean up their session"""
        try:
            if client_id in self.active_connections:
                websocket = self.active_connections[client_id]
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket.close()
                del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected and cleaned up")
        except Exception as e:
            logger.error(f"Error during client {client_id} cleanup: {str(e)}")

    async def send_market_data(self, client_id: str, data: Dict[str, Any]):
        """Send market data to a specific client"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket.send_json(data)
                else:
                    await self.disconnect(client_id)
            except Exception as e:
                logger.error(f"Error sending market data to {client_id}: {str(e)}")
                await self.disconnect(client_id)

async def market_data_callback(data: Dict[str, Any]):
    """Callback function for market data updates"""
    for client_id in list(manager.active_connections.keys()):
        await manager.send_market_data(client_id, {
            "type": "MARKET_DATA",
            "data": data
        })

manager = ConnectionManager()

@router.websocket("/options/{symbol}/{expiry}")
async def websocket_endpoint(
    websocket: WebSocket,
    symbol: str,
    expiry: str,
    token: str = Query(...)
):
    """WebSocket endpoint for real-time market data"""
    client_id = f"{symbol}_{expiry}_{datetime.now().timestamp()}"
    
    try:
        # Connect client
        await manager.connect(websocket, client_id, token)
        logger.info(f"Client {client_id} connected for {symbol} {expiry}")

        # Get initial option chain data
        try:
            chain = await manager.kite_service.get_option_chain(symbol, expiry)
            await websocket.send_json({
                "type": "OPTION_CHAIN",
                "data": chain
            })
        except Exception as e:
            logger.error(f"Error fetching initial option chain: {e}")
            await websocket.send_json({
                "type": "ERROR",
                "error": str(e)
            })

        # Add market data callback
        manager.kite_service.add_market_data_callback(market_data_callback)
        
        try:
            while True:
                data = await websocket.receive_json()
                logger.debug(f"Received data from client {client_id}: {data}")
                
                if data.get("type") == "subscribe":
                    try:
                        if "instruments" in data:
                            tokens = data["instruments"]
                            if tokens:
                                manager.kite_service.subscribe(tokens)
                                await websocket.send_json({
                                    "type": "SUCCESS",
                                    "message": "Subscribed to instruments"
                                })
                    except Exception as e:
                        logger.error(f"Error subscribing to instruments: {e}")
                        await websocket.send_json({
                            "type": "ERROR",
                            "error": str(e)
                        })
                
        except WebSocketDisconnect:
            logger.info(f"Client {client_id} disconnected")
        finally:
            await manager.disconnect(client_id)
            manager.kite_service.remove_market_data_callback(market_data_callback)
            
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close(code=4000, reason=str(e))
    finally:
        # Clean up
        if client_id in manager.active_connections:
            await manager.disconnect(client_id)
