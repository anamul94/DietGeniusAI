from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import AsyncGenerator, Optional
import json
import asyncio
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.meal_plan import generate_meal_plan_streaming
from app.core.logging import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

async def meal_plan_stream_generator(
    user_id: int,
    session_id: str,
    db: Session
) -> AsyncGenerator[str, None]:
    """Generate streaming meal plan response"""
    try:
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connection', 'message': 'Connected to meal plan generator'})}\n\n"
        
        # Stream meal plan generation
        async for chunk in generate_meal_plan_streaming(user_id, session_id, db):
            if chunk.get('type') == 'chunk':
                yield f"data: {json.dumps(chunk)}\n\n"
            elif chunk.get('type') == 'complete':
                yield f"data: {json.dumps(chunk)}\n\n"
                break
            elif chunk.get('type') == 'error':
                yield f"data: {json.dumps(chunk)}\n\n"
                break
                
        # Send completion message
        yield f"data: {json.dumps({'type': 'done', 'message': 'Meal plan generation complete'})}\n\n"
        
    except Exception as e:
        logger.error(f"Error in meal plan streaming: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    finally:
        yield f"data: {json.dumps({'type': 'close', 'message': 'Connection closing'})}\n\n"


@router.get("/meal-plans/stream")
async def stream_meal_plan(
    session_id: str = Query(..., description="Session ID for tracking the stream"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Stream meal plan generation using Server-Sent Events (SSE)
    
    This endpoint provides real-time streaming of meal plan generation progress.
    Each line is a Server-Sent Event with JSON data.
    
    Example usage:
    ```javascript
    const eventSource = new EventSource('/api/streaming/meal-plans/stream?session_id=123');
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data);
    };
    ```
    """
    return StreamingResponse(
        meal_plan_stream_generator(current_user.id, session_id, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        }
    )


async def test_stream_generator() -> AsyncGenerator[str, None]:
    """Test streaming endpoint"""
    for i in range(10):
        data = {
            "type": "progress",
            "message": f"Processing step {i + 1}/10",
            "progress": (i + 1) * 10,
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(1)
    
    yield f"data: {json.dumps({'type': 'complete', 'message': 'Test completed'})}\n\n"


@router.get("/test-stream")
async def test_stream():
    """Test streaming endpoint without authentication"""
    return StreamingResponse(
        test_stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


@router.post("/meal-plans/generate-streaming")
async def generate_meal_plan_streaming_post(
    session_id: str = Query(..., description="Session ID for tracking the stream"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Alternative POST endpoint for streaming meal plan generation
    Useful for clients that need to send larger payloads
    """
    return StreamingResponse(
        meal_plan_stream_generator(current_user.id, session_id, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )