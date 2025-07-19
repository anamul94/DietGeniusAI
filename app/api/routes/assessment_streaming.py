from datetime import date
import asyncio
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user_from_token
from app.models.user import User
from app.services.daily_activity_summary import daily_activity_assessment_by_ai_nutritionis
from app.core.logging import logger
from app.agents.agetns import get_memory_test_agent
router = APIRouter()

# Store active SSE connections by session_id
active_connections = {}

async def generate_assessment_stream(
    db: Session,
    user_id: int,
    user_name: str,
    target_date: Optional[date],
    session_id: str
):
    """Generate assessment with streaming chunks."""
    
    try:
        # Send initial connection message with keep-alive
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Starting assessment generation...'})}\n\n"
        yield f"retry: 3000\n\n"  # Tell client to retry after 3 seconds on error
        await asyncio.sleep(0.1)
        
        # Send progress updates
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Initializing memory test agent...', 'progress': 10})}\n\n"
        await asyncio.sleep(0.5)
        
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Preparing assessment context...', 'progress': 30})}\n\n"
        await asyncio.sleep(0.5)
        
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Generating AI assessment...', 'progress': 50})}\n\n"
        
        # Initialize memory test agent and stream response
        agent = get_memory_test_agent()
        full_response = ""
        chunk_index = 0
        
        # Stream response from memory test agent
        try:
            for response in agent.run(
                message="Generate a comprehensive memory and cognitive assessment based on the user's daily activity and nutrition patterns",
                stream=True
            ):
                if response is not None and hasattr(response, 'content'):
                    content = response.content
                    if content:
                        full_response += content
                        yield f"data: {json.dumps({'type': 'chunk', 'data': content, 'chunk_index': chunk_index})}\n\n"
                        chunk_index += 1
                        await asyncio.sleep(0.05)  # Small delay for smooth streaming
                        
                        # Send keep-alive every 10 chunks
                        if chunk_index % 10 == 0:
                            yield f"data: {json.dumps({'type': 'keepalive', 'timestamp': str(date.today())})}\n\n"
                            
        except Exception as agent_error:
            logger.error(f"Error in agent streaming: {str(agent_error)}")
            yield f"data: {json.dumps({'type': 'error', 'message': f"AI agent error: {str(agent_error)}"})}\n\n"
            return
            
        # Send final progress update
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Finalizing assessment...', 'progress': 100})}\n\n"
        await asyncio.sleep(0.1)
        
        # Send final complete response
        final_response = {
            'type': 'complete',
            'date_value': target_date.isoformat() if target_date else date.today().isoformat(),
            'summary': full_response[:500] + "..." if len(full_response) > 500 else full_response,
            'full_response': full_response
        }
        
        yield f"data: {json.dumps(final_response)}\n\n"
        yield f"event: end\ndata: {json.dumps({'type': 'end'})}\n\n"
        
        # Add a small delay to ensure the client receives the complete message
        await asyncio.sleep(0.5)
        
    except asyncio.CancelledError:
        logger.warning(f"Assessment streaming cancelled for session {session_id}")
        yield f"data: {json.dumps({'type': 'error', 'message': 'Assessment generation cancelled'})}\n\n"
        
    except Exception as e:
        logger.error(f"Error in assessment streaming: {str(e)}", exc_info=True)
        error_response = {
            'type': 'error',
            'message': f"Error generating assessment: {str(e)}"
        }
        yield f"data: {json.dumps(error_response)}\n\n"
    
    finally:
        # Clean up connection
        if session_id in active_connections:
            del active_connections[session_id]
        
        # Send final close signal
        yield f"data: {json.dumps({'type': 'close'})}\n\n"

@router.get("/stream-assessment")
async def stream_daily_assessment(
    session_id: str = Query(..., description="Session ID for tracking the stream"),
    target_date: Optional[date] = Query(
        default=None,
        description="Target date for assessment (defaults to today)",
        example="2025-07-15"
    ),
    token: str = Query(..., description="JWT token for authentication"),
    db: Session = Depends(get_db)
):
    """
    Stream daily assessment generation using Server-Sent Events.
    
    This endpoint provides real-time updates as the AI generates the daily assessment:
    1. Progress updates (10%, 30%, 50%, 70%, 90%)
    2. Chunks of the assessment as they're generated
    3. Final complete assessment
    
    **Query Parameters:**
    - `session_id`: Unique session identifier for tracking
    - `target_date`: Date for assessment (optional, defaults to today)
    - `token`: JWT authentication token
    
    **SSE Events:**
    - `connected`: Initial connection confirmation
    - `progress`: Progress updates with percentage
    - `chunk`: Assessment chunks (200 characters each)
    - `complete`: Final complete assessment
    - `error`: Error messages
    
    **Example Usage:**
    ```javascript
    const eventSource = new EventSource(
      '/api/assessment-streaming/stream-assessment?session_id=123&target_date=2025-07-15&token=your-jwt-token'
    );
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'chunk') {
        // Append chunk to UI
      } else if (data.type === 'complete') {
        // Replace with full response
      }
    };
    ```
    """
    
    # Validate token and get user
    try:
        current_user = get_current_user_from_token(token, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    @router.options("/stream-assessment")
    async def stream_assessment_options():
        """Handle CORS preflight requests for the stream-assessment endpoint."""
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Authorization, Content-Type, Cache-Control",
                "Access-Control-Allow-Credentials": "true",
            }
        )
    
    # Register this session
    active_connections[session_id] = {
        'user_id': current_user.id,
        'target_date': target_date
    }
    
    return StreamingResponse(
        generate_assessment_stream(
            db=db,
            user_id=current_user.id,
            user_name=current_user.username,
            target_date=target_date,
            session_id=session_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Cache-Control",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Credentials": "true",
            "X-Accel-Buffering": "no",  # Disable proxy buffering
            "Content-Type": "text/event-stream; charset=utf-8",
        }
    )

@router.post("/trigger-assessment-stream")
async def trigger_assessment_stream(
    session_id: str = Query(..., description="Session ID for tracking the stream"),
    target_date: Optional[date] = Query(
        default=None,
        description="Target date for assessment (defaults to today)",
        example="2025-07-15"
    ),
    token: str = Query(..., description="JWT token for authentication"),
    db: Session = Depends(get_db)
):
    """
    Alternative POST endpoint to trigger assessment streaming.
    
    Useful for cases where you need to send additional data in the request body
    or when GET requests are not suitable.
    """
    
    # Validate token and get user
    try:
        current_user = get_current_user_from_token(token, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    return {"message": "Assessment stream triggered", "session_id": session_id}

@router.get("/test-auth")
async def test_auth(
    token: str = Query(..., description="JWT token for authentication"),
    db: Session = Depends(get_db)
):
    """Test endpoint to verify authentication is working."""
    try:
        current_user = get_current_user_from_token(token, db)
        return {
            "authenticated": True,
            "user_id": current_user.id,
            "username": current_user.username
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )