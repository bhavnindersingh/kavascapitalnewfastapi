from fastapi import APIRouter, Depends, HTTPException, WebSocket, Query
from services.kite_service import KiteService
from services.websocket_service import WebSocketManager
from typing import List
import uuid

router = APIRouter(prefix="/api/v1/kite")
websocket_manager = WebSocketManager()

def get_kite_service():
    return KiteService()

@router.get("/login")
async def login(kite_service: KiteService = Depends(get_kite_service)):
    """Get Kite Connect login URL"""
    return {"login_url": kite_service.get_login_url()}

@router.get("/callback")
async def callback(
    request_token: str,
    kite_service: KiteService = Depends(get_kite_service)
):
    """Handle Kite Connect callback after login"""
    return await kite_service.set_access_token(request_token)

@router.get("/validate")
async def validate_token(kite_service: KiteService = Depends(get_kite_service)):
    """Validate access token"""
    is_valid = kite_service.validate_token()
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"status": "valid"}

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str = None,
    instruments: List[int] = Query(None)
):
    """WebSocket endpoint for real-time market data"""
    if not client_id:
        client_id = str(uuid.uuid4())
    
    try:
        await websocket_manager.connect(websocket, client_id)
        
        if instruments:
            websocket_manager.subscribe(client_id, instruments)
        
        try:
            while True:
                data = await websocket.receive_text()
                # Handle incoming messages if needed
        except Exception as e:
            print(f"WebSocket error: {str(e)}")
        finally:
            websocket_manager.disconnect(client_id)
    except Exception as e:
        print(f"Failed to establish WebSocket connection: {str(e)}")

@router.post("/subscribe/{client_id}")
async def subscribe(
    client_id: str,
    instruments: List[int]
):
    """Subscribe to instruments"""
    websocket_manager.subscribe(client_id, instruments)
    return {"status": "subscribed", "instruments": instruments}

@router.post("/unsubscribe/{client_id}")
async def unsubscribe(
    client_id: str,
    instruments: List[int]
):
    """Unsubscribe from instruments"""
    websocket_manager.unsubscribe(client_id, instruments)
    return {"status": "unsubscribed", "instruments": instruments}
