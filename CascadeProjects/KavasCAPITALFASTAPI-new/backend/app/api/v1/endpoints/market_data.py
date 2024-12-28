from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.db.session import get_db
from app.services.market_data_service import MarketDataService
from app.schemas.market_data import (
    KiteTick, MarketDepth, WebSocketSubscription,
    InstrumentType, OptionInstrument, FutureInstrument
)
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter(tags=["market-data"])

# Initialize market data service
market_data_service = MarketDataService()

@router.post("/subscribe")
async def subscribe_instruments(
    subscription: WebSocketSubscription,
    db: AsyncSession = Depends(get_db)
):
    """Subscribe to market data for instruments."""
    try:
        await market_data_service.subscribe_instruments(subscription.tokens, subscription.mode)
        return {"status": "success", "message": "Subscribed successfully"}
    except Exception as e:
        logger.error(f"Error subscribing to instruments: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/unsubscribe")
async def unsubscribe_instruments(
    subscription: WebSocketSubscription,
    db: AsyncSession = Depends(get_db)
):
    """Unsubscribe from market data for instruments."""
    try:
        await market_data_service.unsubscribe_instruments(subscription.tokens)
        return {"status": "success", "message": "Unsubscribed successfully"}
    except Exception as e:
        logger.error(f"Error unsubscribing from instruments: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tick/{instrument_token}")
async def get_latest_tick(
    instrument_token: int,
    db: AsyncSession = Depends(get_db)
):
    """Get latest tick data for an instrument."""
    try:
        tick = await market_data_service.get_latest_tick(instrument_token)
        if not tick:
            raise HTTPException(status_code=404, detail="Tick data not found")
        return tick
    except Exception as e:
        logger.error(f"Error getting latest tick: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/depth/{instrument_token}")
async def get_market_depth(
    instrument_token: int,
    db: AsyncSession = Depends(get_db)
):
    """Get market depth for an instrument."""
    try:
        depth = await market_data_service.get_latest_depth(instrument_token)
        if not depth:
            raise HTTPException(status_code=404, detail="Market depth not found")
        return depth
    except Exception as e:
        logger.error(f"Error getting market depth: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.websocket("/ws/market-data")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    """WebSocket endpoint for real-time market data."""
    await websocket.accept()
    
    async def send_tick(tick: KiteTick):
        try:
            await websocket.send_json(tick.dict())
        except Exception as e:
            logger.error(f"Error sending tick data: {e}")
    
    try:
        # Add callback for sending data to this client
        market_data_service.add_tick_callback(send_tick)
        
        while True:
            try:
                # Wait for subscription/unsubscription messages
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message["action"] == "subscribe":
                    subscription = WebSocketSubscription(**message["data"])
                    await market_data_service.subscribe_instruments(
                        subscription.tokens,
                        subscription.mode
                    )
                    await websocket.send_json({
                        "status": "success",
                        "message": "Subscribed successfully"
                    })
                    
                elif message["action"] == "unsubscribe":
                    subscription = WebSocketSubscription(**message["data"])
                    await market_data_service.unsubscribe_instruments(subscription.tokens)
                    await websocket.send_json({
                        "status": "success",
                        "message": "Unsubscribed successfully"
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "status": "error",
                    "message": "Invalid message format"
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Clean up on disconnect
        if send_tick in market_data_service.tick_callbacks:
            market_data_service.tick_callbacks.remove(send_tick)
