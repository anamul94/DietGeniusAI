from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websockets.handlers import websocket_endpoint, test_websocket_endpoint

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_route(websocket: WebSocket, user_id: str, token: str = Query(...)):
    """WebSocket endpoint for authenticated users"""
    await websocket_endpoint(websocket, user_id, token)

@router.websocket("/test-ws-simple")
async def test_websocket_route(websocket: WebSocket):
    """Simple test WebSocket endpoint without authentication"""
    await test_websocket_endpoint(websocket)