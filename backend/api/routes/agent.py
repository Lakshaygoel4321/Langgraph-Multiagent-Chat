from fastapi import APIRouter, HTTPException, status, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, AsyncGenerator, List
import json
import asyncio
from datetime import datetime
import uuid

from src.graph.workflow import AgentWorkflow


router = APIRouter()

# Initialize workflow (singleton pattern)
workflow = AgentWorkflow()


# Request/Response Models
class QuestionRequest(BaseModel):
    """Request model for question submission"""
    question: str = Field(..., min_length=1, max_length=2000, description="User question")
    thread_id: Optional[str] = Field(default=None, description="Conversation thread ID for memory")
    stream: bool = Field(default=False, description="Enable streaming response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is SWOT analysis?",
                "thread_id": "user-123-session-1",
                "stream": False
            }
        }


class AgentResponse(BaseModel):
    """Response model for agent answer"""
    question: str
    answer: str
    confidence_score: str
    classifier: str
    reasoning: str
    timestamp: str
    thread_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is SWOT analysis?",
                "answer": "SWOT analysis is a strategic planning tool...",
                "confidence_score": "9",
                "classifier": "business",
                "reasoning": "Question relates to business strategy",
                "timestamp": "2025-12-25T12:00:00Z",
                "thread_id": "user-123-session-1"
            }
        }


class ConversationHistory(BaseModel):
    """Model for conversation history"""
    thread_id: str
    messages: List[Dict[str, Any]]
    total_interactions: int


class StreamChunk(BaseModel):
    """Streaming chunk model"""
    event: str
    data: Dict[str, Any]
    timestamp: str


# API Endpoints

@router.post("/ask", response_model=AgentResponse, status_code=status.HTTP_200_OK)
async def ask_question(request: QuestionRequest):
    """
    Submit a question to the multi-agent system (non-streaming)
    
    Args:
        request: Question request with question text and optional thread_id
        
    Returns:
        Complete agent response with answer and metadata
    """
    try:
        if not request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty"
            )
        
        # Generate thread_id if not provided
        thread_id = request.thread_id or f"thread-{uuid.uuid4()}"
        
        # Execute workflow with thread_id
        result = await asyncio.to_thread(
            workflow.invoke, 
            request.question, 
            thread_id
        )
        
        # Extract response data
        response = AgentResponse(
            question=request.question,
            answer=result.get("final_data", "No answer generated"),
            confidence_score=result.get("validator_score", "N/A"),
            classifier=result.get("classifier_response", "unknown"),
            reasoning=result.get("region_response", "No reasoning provided"),
            timestamp=datetime.utcnow().isoformat() + "Z",
            thread_id=thread_id
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )


@router.post("/ask/stream")
async def ask_question_stream(request: QuestionRequest):
    """
    Submit a question to the multi-agent system (streaming)
    
    Args:
        request: Question request with question text and optional thread_id
        
    Returns:
        Server-Sent Events (SSE) stream of agent workflow
    """
    try:
        if not request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty"
            )
        
        # Generate thread_id if not provided
        thread_id = request.thread_id or f"thread-{uuid.uuid4()}"
        
        async def event_generator() -> AsyncGenerator[str, None]:
            """Generate SSE events from workflow stream"""
            try:
                # Send start event with thread_id
                yield f"data: {json.dumps({'event': 'start', 'data': {'question': request.question, 'thread_id': thread_id}, 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                
                # Stream workflow execution with thread_id
                for output in workflow.stream(request.question, thread_id):
                    for node_name, node_data in output.items():
                        chunk = {
                            "event": "node_complete",
                            "data": {
                                "node": node_name,
                                "content": str(node_data.get("final_data", ""))[:500],
                                "classifier": node_data.get("classifier_response", ""),
                                "score": node_data.get("validator_score", ""),
                                "thread_id": thread_id
                            },
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        yield f"data: {json.dumps(chunk)}\n\n"
                        await asyncio.sleep(0.01)
                
                # Send completion event
                yield f"data: {json.dumps({'event': 'complete', 'data': {'status': 'finished', 'thread_id': thread_id}, 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                
            except Exception as e:
                error_chunk = {
                    "event": "error",
                    "data": {"message": str(e), "thread_id": thread_id},
                    "timestamp": datetime.utcnow().isoformat()
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error streaming question: {str(e)}"
        )


@router.get("/history/{thread_id}", response_model=ConversationHistory)
async def get_conversation_history(
    thread_id: str,
    limit: int = 10
):
    """
    Get conversation history for a specific thread
    
    Args:
        thread_id: Conversation thread identifier
        limit: Maximum number of history items (default: 10)
        
    Returns:
        Conversation history with messages
    """
    try:
        history = await asyncio.to_thread(
            workflow.get_state_history,
            thread_id,
            limit
        )
        
        messages = []
        for state_snapshot in history:
            if hasattr(state_snapshot, 'values') and state_snapshot.values:
                messages.append({
                    "question": state_snapshot.values.get("question", ""),
                    "answer": state_snapshot.values.get("final_data", ""),
                    "classifier": state_snapshot.values.get("classifier_response", ""),
                    "confidence": state_snapshot.values.get("validator_score", ""),
                })
        
        return ConversationHistory(
            thread_id=thread_id,
            messages=messages,
            total_interactions=len(messages)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching history: {str(e)}"
        )


@router.get("/state/{thread_id}")
async def get_thread_state(thread_id: str):
    """
    Get current state of a conversation thread
    
    Args:
        thread_id: Conversation thread identifier
        
    Returns:
        Current thread state
    """
    try:
        state = await asyncio.to_thread(workflow.get_state, thread_id)
        
        if state is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Thread {thread_id} not found"
            )
        
        return {
            "thread_id": thread_id,
            "state": state.values if hasattr(state, 'values') else {},
            "next": state.next if hasattr(state, 'next') else []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching state: {str(e)}"
        )


@router.get("/status")
async def get_status():
    """Get API status and configuration"""
    return {
        "status": "operational",
        "model": "llama-3.3-70b-versatile",
        "available_agents": ["business", "research", "technical"],
        "features": {
            "streaming": True,
            "synthesis": True,
            "validation": True,
            "memory": True,
            "checkpointer": "MemorySaver"
        }
    }
