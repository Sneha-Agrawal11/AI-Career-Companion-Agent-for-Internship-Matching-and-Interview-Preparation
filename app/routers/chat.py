from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, ChatSession, ChatMessage
from app.schemas import ChatSessionCreate, ChatSessionResponse, ChatMessageCreate, ChatMessageResponse
from app.dependencies import get_current_user
from app.services.chat_service import chat_service

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_user_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all chat sessions for the authenticated user."""
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.updated_at.desc()).all()
    return sessions

@router.post("/sessions", response_model=ChatSessionResponse)
def create_session(
    session_in: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat session for the authenticated user."""
    db_session = ChatSession(
        user_id=current_user.id,
        title=session_in.title
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all messages for a specific session."""
    # Verify ownership
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or you do not have permission")
        
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    return messages

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
def send_message(
    session_id: int,
    message_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message, retrieve context, generate AI response, and store both."""
    # Verify ownership
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or you do not have permission")
    
    # Store user message
    user_message = ChatMessage(
        session_id=session_id,
        user_id=current_user.id,
        role="user",
        message=message_in.message
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Fetch recent history for LLM context (e.g., last 20 messages)
    history_records = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id, 
        ChatMessage.id <= user_message.id
    ).order_by(ChatMessage.created_at.desc()).limit(20).all()
    
    # Reverse to chronological order
    history_records.reverse()
    
    # Exclude the current message we just added from history, format for LLM
    chat_history = [{"role": m.role, "message": m.message} for m in history_records[:-1]]
    
    # Generate AI response via service
    ai_text = chat_service.generate_response(user_message.message, chat_history)
    
    # Store AI message
    ai_message = ChatMessage(
        session_id=session_id,
        user_id=current_user.id, # Keep tied to the user
        role="assistant",
        message=ai_text
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    # Update session updated_at
    from datetime import datetime
    session.updated_at = datetime.utcnow()
    # Update title if it's the first message
    if len(history_records) == 1 and session.title == "New Chat":
        # simple title generation: first 30 chars
        session.title = message_in.message[:30] + ("..." if len(message_in.message) > 30 else "")
    
    db.commit()
    
    return ai_message
