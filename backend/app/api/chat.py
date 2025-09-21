"""Chat API endpoints for jurisdiction-aware document interaction."""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.ai_analysis_service import AIAnalysisService
from app.services.document_service import DocumentService
from app.core.dependencies import get_current_user
from app.database.models.user import User
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatStreamRequest,
    JurisdictionContextResponse
)
from app.core.exceptions import AIProcessingError, InvalidInputError


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


# Initialize services
ai_service = AIAnalysisService()
document_service = DocumentService()


class ChatSessionManager:
    """Manages chat sessions and conversation state."""
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(
        self,
        user_id: str,
        document_id: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        title: Optional[str] = None
    ) -> str:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        
        self._sessions[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "document_id": document_id,
            "jurisdiction": jurisdiction,
            "title": title or f"Chat Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "metadata": {}
        }
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get chat session by ID."""
        return self._sessions.get(session_id)
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add message to session."""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        message_id = str(uuid.uuid4())
        message = {
            "id": message_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        self._sessions[session_id]["messages"].append(message)
        self._sessions[session_id]["updated_at"] = datetime.utcnow()
        
        return message_id
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user."""
        return [
            session for session in self._sessions.values()
            if session["user_id"] == user_id
        ]
    
    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a session (only by owner)."""
        session = self._sessions.get(session_id)
        if not session or session["user_id"] != user_id:
            return False
        
        del self._sessions[session_id]
        return True


# Global session manager instance
session_manager = ChatSessionManager()


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat session."""
    try:
        # Validate document if provided
        document = None
        if session_data.document_id:
            document = await document_service.get_document(
                session_data.document_id, current_user.id, db
            )
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
        
        # Determine jurisdiction
        jurisdiction = session_data.jurisdiction
        if not jurisdiction and document:
            # Try to get jurisdiction from document metadata
            if hasattr(document, 'metadata') and document.metadata:
                jurisdiction = getattr(document.metadata, 'jurisdiction', None)
        
        # Create session
        session_id = session_manager.create_session(
            user_id=current_user.id,
            document_id=session_data.document_id,
            jurisdiction=jurisdiction,
            title=session_data.title
        )
        
        session = session_manager.get_session(session_id)
        
        return ChatSessionResponse(
            id=session["id"],
            title=session["title"],
            document_id=session["document_id"],
            jurisdiction=session["jurisdiction"],
            message_count=len(session["messages"]),
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            is_active=session["is_active"]
        )
        
    except Exception as e:
        logger.error(f"Failed to create chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create chat session")


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_user_chat_sessions(
    current_user: User = Depends(get_current_user)
):
    """Get all chat sessions for the current user."""
    try:
        sessions = session_manager.get_user_sessions(current_user.id)
        
        return [
            ChatSessionResponse(
                id=session["id"],
                title=session["title"],
                document_id=session["document_id"],
                jurisdiction=session["jurisdiction"],
                message_count=len(session["messages"]),
                created_at=session["created_at"],
                updated_at=session["updated_at"],
                is_active=session["is_active"]
            )
            for session in sorted(sessions, key=lambda x: x["updated_at"], reverse=True)
        ]
        
    except Exception as e:
        logger.error(f"Failed to get chat sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get chat sessions")


@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific chat session with messages."""
    try:
        session = session_manager.get_session(session_id)
        
        if not session or session["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session": {
                "id": session["id"],
                "title": session["title"],
                "document_id": session["document_id"],
                "jurisdiction": session["jurisdiction"],
                "created_at": session["created_at"],
                "updated_at": session["updated_at"],
                "is_active": session["is_active"]
            },
            "messages": [
                {
                    "id": msg["id"],
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg["timestamp"],
                    "metadata": msg["metadata"]
                }
                for msg in session["messages"]
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get chat session")


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    session_id: str,
    message_data: ChatMessageCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message in a chat session and get AI response."""
    try:
        # Validate session
        session = session_manager.get_session(session_id)
        if not session or session["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Add user message
        user_message_id = session_manager.add_message(
            session_id=session_id,
            role="user",
            content=message_data.content,
            metadata={
                "jurisdiction": message_data.jurisdiction,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Get document content if available
        document_content = None
        if session["document_id"]:
            document = await document_service.get_document(
                session["document_id"], current_user.id, db
            )
            if document and hasattr(document, 'content'):
                document_content = document.content
        
        # Generate AI response
        ai_response = await ai_service.chat_with_document(
            session_id=session_id,
            question=message_data.content,
            document_content=document_content,
            user_id=current_user.id,
            jurisdiction=message_data.jurisdiction or session["jurisdiction"]
        )
        
        # Parse AI response for structured data
        response_metadata = {
            "confidence": ai_response.get("metadata", {}).get("confidence"),
            "jurisdiction": ai_response.get("metadata", {}).get("jurisdiction"),
            "processing_time": ai_response.get("metadata", {}).get("processing_time"),
            "token_usage": ai_response.get("metadata", {}).get("token_usage"),
            "model": ai_response.get("metadata", {}).get("model"),
            "references": ai_response.get("parsed_response", {}).get("citations", [])
        }
        
        # Add AI response message
        ai_message_id = session_manager.add_message(
            session_id=session_id,
            role="assistant",
            content=ai_response["response"],
            metadata=response_metadata
        )
        
        return ChatMessageResponse(
            id=ai_message_id,
            role="assistant",
            content=ai_response["response"],
            timestamp=datetime.utcnow(),
            jurisdiction=message_data.jurisdiction or session["jurisdiction"],
            confidence=response_metadata.get("confidence"),
            references=response_metadata.get("references", []),
            metadata=response_metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send chat message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process message")


@router.post("/sessions/{session_id}/stream")
async def stream_chat_response(
    session_id: str,
    stream_request: ChatStreamRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stream AI response for real-time chat experience."""
    try:
        # Validate session
        session = session_manager.get_session(session_id)
        if not session or session["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get document content if available
        document_content = None
        if session["document_id"]:
            document = await document_service.get_document(
                session["document_id"], current_user.id, db
            )
            if document and hasattr(document, 'content'):
                document_content = document.content
        
        async def generate_stream():
            """Generate streaming response."""
            try:
                # Add user message to session
                session_manager.add_message(
                    session_id=session_id,
                    role="user",
                    content=stream_request.message,
                    metadata={
                        "jurisdiction": stream_request.jurisdiction,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                # Stream AI response
                full_response = ""
                async for chunk in ai_service.stream_chat_response(
                    session_id=session_id,
                    question=stream_request.message,
                    document_content=document_content,
                    user_id=current_user.id,
                    jurisdiction=stream_request.jurisdiction or session["jurisdiction"]
                ):
                    full_response += chunk
                    yield f"data: {chunk}\n\n"
                
                # Add complete response to session
                session_manager.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=full_response,
                    metadata={
                        "jurisdiction": stream_request.jurisdiction or session["jurisdiction"],
                        "timestamp": datetime.utcnow().isoformat(),
                        "streaming": True
                    }
                )
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Streaming error: {str(e)}")
                yield f"data: Error: {str(e)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start streaming: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start streaming")


@router.get("/sessions/{session_id}/context", response_model=JurisdictionContextResponse)
async def get_jurisdiction_context(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get jurisdiction-specific context for the chat session."""
    try:
        # Validate session
        session = session_manager.get_session(session_id)
        if not session or session["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get document and jurisdiction info
        document = None
        if session["document_id"]:
            document = await document_service.get_document(
                session["document_id"], current_user.id, db
            )
        
        jurisdiction = session["jurisdiction"]
        if not jurisdiction and document and hasattr(document, 'metadata'):
            jurisdiction = getattr(document.metadata, 'jurisdiction', None)
        
        # Get jurisdiction-specific suggestions and context
        suggestions = []
        applicable_laws = []
        compliance_requirements = []
        
        if jurisdiction == "india":
            suggestions = [
                "What is the stamp duty requirement?",
                "Check GST implications",
                "Verify Indian Contract Act compliance",
                "What registration is required?",
                "Analyze enforceability under Indian law"
            ]
            applicable_laws = [
                "Indian Contract Act, 1872",
                "Stamp Act (State-specific)",
                "Goods and Services Tax Act, 2017",
                "Companies Act, 2013"
            ]
            compliance_requirements = [
                "Stamp duty payment",
                "Document registration",
                "GST compliance",
                "Regulatory approvals"
            ]
        elif jurisdiction == "usa":
            suggestions = [
                "Check UCC applicability",
                "Analyze choice of law provisions",
                "Review securities law compliance",
                "Check CCPA privacy requirements",
                "Verify federal law compliance"
            ]
            applicable_laws = [
                "Uniform Commercial Code",
                "Federal Securities Laws",
                "State Contract Law",
                "Privacy Laws (CCPA, etc.)"
            ]
            compliance_requirements = [
                "State law compliance",
                "Federal regulatory compliance",
                "Privacy law adherence",
                "Securities law compliance"
            ]
        elif jurisdiction == "cross_border":
            suggestions = [
                "Compare enforceability across jurisdictions",
                "Analyze tax treaty implications",
                "Review dispute resolution mechanisms",
                "Check cross-border compliance requirements",
                "Evaluate governing law provisions"
            ]
            applicable_laws = [
                "India-US Double Taxation Avoidance Agreement",
                "International Commercial Law",
                "Cross-border Regulatory Framework"
            ]
            compliance_requirements = [
                "Multi-jurisdictional compliance",
                "Tax treaty considerations",
                "International dispute resolution",
                "Cross-border regulatory approvals"
            ]
        
        return JurisdictionContextResponse(
            jurisdiction=jurisdiction,
            confidence=0.9 if jurisdiction else 0.0,
            suggestions=suggestions,
            applicable_laws=applicable_laws,
            compliance_requirements=compliance_requirements,
            document_type=document.type if document else None,
            document_name=document.name if document else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get jurisdiction context: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get jurisdiction context")


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a chat session."""
    try:
        success = session_manager.delete_session(session_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete session")


@router.get("/suggestions/{jurisdiction}")
async def get_jurisdiction_suggestions(
    jurisdiction: str,
    document_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get jurisdiction-specific chat suggestions."""
    try:
        # Get jurisdiction-specific analysis types
        analysis_types = ai_service.get_jurisdiction_specific_analyses(jurisdiction)
        
        # Convert to user-friendly suggestions
        suggestions = []
        for analysis_type in analysis_types:
            if analysis_type == "stamp_duty_calculation":
                suggestions.append({
                    "text": "What is the stamp duty requirement?",
                    "type": "jurisdiction_specific",
                    "category": "Indian Law",
                    "description": "Calculate stamp duty obligations"
                })
            elif analysis_type == "gst_analysis":
                suggestions.append({
                    "text": "Check GST implications",
                    "type": "jurisdiction_specific", 
                    "category": "Tax Law",
                    "description": "Analyze GST applicability"
                })
            elif analysis_type == "ucc_analysis":
                suggestions.append({
                    "text": "Check UCC applicability",
                    "type": "jurisdiction_specific",
                    "category": "US Law",
                    "description": "Uniform Commercial Code analysis"
                })
            # Add more mappings as needed
        
        # Add common suggestions
        common_suggestions = [
            {
                "text": "What are the key risks in this document?",
                "type": "question",
                "category": "Risk Analysis",
                "description": "Analyze potential legal risks"
            },
            {
                "text": "Summarize the main obligations",
                "type": "question",
                "category": "Obligations", 
                "description": "Extract key obligations and duties"
            }
        ]
        
        return {
            "jurisdiction": jurisdiction,
            "suggestions": suggestions + common_suggestions,
            "document_type": document_type
        }
        
    except Exception as e:
        logger.error(f"Failed to get suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get suggestions")