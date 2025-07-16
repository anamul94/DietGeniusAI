from fastapi import WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt
from app.core.config import settings
from app.core.logging import setup_logger
from .manager import manager
from agno.agent import Agent
from agno.models.groq import Groq

logger = setup_logger(__name__)

agent = Agent(
    model=Groq(id="qwen/qwen3-32b")
)
async def get_current_user_from_token(token: str):
    """Extract user ID from JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token: no user ID found")
        return user_id
    except JWTError:
        raise ValueError("Invalid token")


async def websocket_endpoint(websocket: WebSocket, user_id: str, token: str):
    """WebSocket endpoint for real-time communication"""
    try:
        # Validate token and get user ID
        token_user_id = await get_current_user_from_token(token)
        
        # Ensure the user_id in the path matches the token
        if str(user_id) != str(token_user_id):
            await websocket.close(code=1008, reason="User ID mismatch")
            return
            
    except ValueError as e:
        await websocket.close(code=1008, reason=str(e))
        return

    # Accept the connection
    await manager.connect(websocket, str(user_id))
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            try:
                for chunk in agent.run(
                    message=data,
                ):
                    
                    message = {"type": "chunk", "data": chunk, "from": "server"}
                    await manager.send_personal_message(message, str(user_id))
                # message = {"type": "echo", "data": data, "from": "server"}
                await manager.send_personal_message(message, str(user_id))
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, str(user_id))
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, str(user_id))


async def test_websocket_endpoint(websocket: WebSocket):
    """Simple test WebSocket endpoint without authentication"""
    await websocket.accept()
    try:
        await websocket.send_text('{"type": "test", "message": "WebSocket connection successful!"}')
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f'{{"type": "echo", "data": {data}}}')
    except WebSocketDisconnect:
        logger.info("Test WebSocket disconnected")