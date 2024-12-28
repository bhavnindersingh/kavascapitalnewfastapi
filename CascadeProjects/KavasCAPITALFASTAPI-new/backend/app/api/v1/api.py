from fastapi import APIRouter
from app.api.v1 import websocket, options

api_router = APIRouter()

# Include WebSocket routes
api_router.include_router(websocket.router, tags=["websocket"])

# Include Options routes
api_router.include_router(options.router, prefix="/options", tags=["options"])
