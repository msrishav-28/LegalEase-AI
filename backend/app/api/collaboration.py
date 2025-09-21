"""Collaboration API endpoints for real-time document collaboration."""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid

from app.core.dependencies import get_current_user, get_db
from app.services.collaboration_service import CollaborationService
from app.schemas.collaboration import (
    DocumentSessionCreate,
    DocumentSessionResponse,
    DocumentAnnotationCreate,
    DocumentAnnotationUpdate,
    DocumentAnnotationResponse,
    SessionParticipantResponse,
    CollaborationEventResponse,
    CursorPosition
)
from app.api.websocket import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/collaboration", tags=["Collaboration"])


# Session Management Endpoints

@router.post("/sessions", response_model=DocumentSessionResponse)
async def create_collaboration_session(
    session_data: DocumentSessionCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new document collaboration session."""
    try:
        collaboration_service = CollaborationService(db)
        
        session = await collaboration_service.create_session(
            session_data,
            current_user.id
        )
        
        # Convert to response format
        return DocumentSessionResponse(
            id=session.id,
            document_id=session.document_id,
            name=session.name,
            is_active=session.is_active,
            created_by=session.created_by,
            created_at=session.created_at,
            updated_at=session.updated_at,
            participants=[],
            annotations=[]
        )
        
    except Exception as e:
        logger.error(f"Failed to create collaboration session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=DocumentSessionResponse)
async def get_collaboration_session(
    session_id: uuid.UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get collaboration session details with participants and annotations."""
    try:
        collaboration_service = CollaborationService(db)
        
        session = await collaboration_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        participants = await collaboration_service.get_session_participants(session_id)
        annotations = await collaboration_service.get_session_annotations(session_id)
        
        # Convert participants to response format
        participant_responses = []
        for p in participants:
            participant_responses.append(SessionParticipantResponse(
                id=p.id,
                user_id=p.user_id,
                user_name=p.user.name if hasattr(p, 'user') and p.user else f"User {p.user_id}",
                user_email=p.user.email if hasattr(p, 'user') and p.user else "",
                joined_at=p.joined_at,
                left_at=p.left_at,
                is_online=p.is_online,
                last_seen=p.last_seen,
                cursor_position=p.cursor_position
            ))
        
        # Convert annotations to response format
        annotation_responses = []
        for a in annotations:
            annotation_responses.append(DocumentAnnotationResponse(
                id=a.id,
                session_id=a.session_id,
                user_id=a.user_id,
                annotation_type=a.annotation_type,
                content=a.content,
                page_number=a.page_number,
                start_offset=a.start_offset,
                end_offset=a.end_offset,
                selected_text=a.selected_text,
                style_data=a.style_data,
                annotation_metadata=a.annotation_metadata,
                is_resolved=a.is_resolved,
                resolved_by=a.resolved_by,
                resolved_at=a.resolved_at,
                created_at=a.created_at,
                updated_at=a.updated_at
            ))
        
        return DocumentSessionResponse(
            id=session.id,
            document_id=session.document_id,
            name=session.name,
            is_active=session.is_active,
            created_by=session.created_by,
            created_at=session.created_at,
            updated_at=session.updated_at,
            participants=participant_responses,
            annotations=annotation_responses
        )
        
    except Exception as e:
        logger.error(f"Failed to get collaboration session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}/sessions", response_model=List[DocumentSessionResponse])
async def get_document_sessions(
    document_id: uuid.UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all collaboration sessions for a document."""
    try:
        collaboration_service = CollaborationService(db)
        
        sessions = await collaboration_service.get_document_sessions(document_id)
        
        session_responses = []
        for session in sessions:
            session_responses.append(DocumentSessionResponse(
                id=session.id,
                document_id=session.document_id,
                name=session.name,
                is_active=session.is_active,
                created_by=session.created_by,
                created_at=session.created_at,
                updated_at=session.updated_at,
                participants=[],
                annotations=[]
            ))
        
        return session_responses
        
    except Exception as e:
        logger.error(f"Failed to get document sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def close_collaboration_session(
    session_id: uuid.UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Close a collaboration session."""
    try:
        collaboration_service = CollaborationService(db)
        
        success = await collaboration_service.close_session(session_id, current_user.id)
        
        if success:
            # Notify WebSocket clients
            await connection_manager.broadcast_to_document_session(
                {
                    "type": "session_closed",
                    "session_id": str(session_id),
                    "closed_by": str(current_user.id),
                    "timestamp": datetime.utcnow().isoformat()
                },
                str(session_id)
            )
        
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Failed to close collaboration session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Participant Management Endpoints

@router.post("/sessions/{session_id}/join")
async def join_collaboration_session(
    session_id: uuid.UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a collaboration session."""
    try:
        collaboration_service = CollaborationService(db)
        
        participant = await collaboration_service.join_session(session_id, current_user.id)
        
        return {
            "success": True,
            "participant": {
                "id": str(participant.id),
                "user_id": str(participant.user_id),
                "joined_at": participant.joined_at.isoformat(),
                "is_online": participant.is_online
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to join collaboration session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/leave")
async def leave_collaboration_session(
    session_id: uuid.UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a collaboration session."""
    try:
        collaboration_service = CollaborationService(db)
        
        success = await collaboration_service.leave_session(session_id, current_user.id)
        
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Failed to leave collaboration session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/participants", response_model=List[SessionParticipantResponse])
async def get_session_participants(
    session_id: uuid.UUID,
    online_only: bool = Query(False, description="Return only online participants"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get participants in a collaboration session."""
    try:
        collaboration_service = CollaborationService(db)
        
        participants = await collaboration_service.get_session_participants(
            session_id, online_only
        )
        
        participant_responses = []
        for p in participants:
            participant_responses.append(SessionParticipantResponse(
                id=p.id,
                user_id=p.user_id,
                user_name=p.user.name if hasattr(p, 'user') and p.user else f"User {p.user_id}",
                user_email=p.user.email if hasattr(p, 'user') and p.user else "",
                joined_at=p.joined_at,
                left_at=p.left_at,
                is_online=p.is_online,
                last_seen=p.last_seen,
                cursor_position=p.cursor_position
            ))
        
        return participant_responses
        
    except Exception as e:
        logger.error(f"Failed to get session participants: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sessions/{session_id}/presence")
async def update_user_presence(
    session_id: uuid.UUID,
    cursor_position: Optional[CursorPosition] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user presence and cursor position in a session."""
    try:
        collaboration_service = CollaborationService(db)
        
        success = await collaboration_service.update_user_presence(
            session_id, current_user.id, cursor_position
        )
        
        if success and cursor_position:
            # Broadcast cursor update via WebSocket
            await connection_manager.update_cursor_position(
                str(session_id), str(current_user.id), cursor_position.dict()
            )
        
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Failed to update user presence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Annotation Management Endpoints

@router.post("/sessions/{session_id}/annotations", response_model=DocumentAnnotationResponse)
async def create_annotation(
    session_id: uuid.UUID,
    annotation_data: DocumentAnnotationCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new annotation in a collaboration session."""
    try:
        collaboration_service = CollaborationService(db)
        
        annotation = await collaboration_service.create_annotation(
            session_id, current_user.id, annotation_data
        )
        
        # Broadcast to WebSocket clients
        await connection_manager.broadcast_to_document_session(
            {
                "type": "annotation_created",
                "session_id": str(session_id),
                "annotation": {
                    "id": str(annotation.id),
                    "user_id": str(annotation.user_id),
                    "annotation_type": annotation.annotation_type,
                    "content": annotation.content,
                    "page_number": annotation.page_number,
                    "start_offset": annotation.start_offset,
                    "end_offset": annotation.end_offset,
                    "selected_text": annotation.selected_text,
                    "style_data": annotation.style_data,
                    "created_at": annotation.created_at.isoformat()
                },
                "timestamp": datetime.utcnow().isoformat()
            },
            str(session_id),
            exclude_user=str(current_user.id)
        )
        
        return DocumentAnnotationResponse(
            id=annotation.id,
            session_id=annotation.session_id,
            user_id=annotation.user_id,
            annotation_type=annotation.annotation_type,
            content=annotation.content,
            page_number=annotation.page_number,
            start_offset=annotation.start_offset,
            end_offset=annotation.end_offset,
            selected_text=annotation.selected_text,
            style_data=annotation.style_data,
            annotation_metadata=annotation.annotation_metadata,
            is_resolved=annotation.is_resolved,
            resolved_by=annotation.resolved_by,
            resolved_at=annotation.resolved_at,
            created_at=annotation.created_at,
            updated_at=annotation.updated_at
        )
        
    except Exception as e:
        logger.error(f"Failed to create annotation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/annotations/{annotation_id}", response_model=DocumentAnnotationResponse)
async def update_annotation(
    annotation_id: uuid.UUID,
    update_data: DocumentAnnotationUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing annotation."""
    try:
        collaboration_service = CollaborationService(db)
        
        annotation = await collaboration_service.update_annotation(
            annotation_id, current_user.id, update_data
        )
        
        if annotation:
            # Broadcast to WebSocket clients
            await connection_manager.broadcast_to_document_session(
                {
                    "type": "annotation_updated",
                    "session_id": str(annotation.session_id),
                    "annotation": {
                        "id": str(annotation.id),
                        "user_id": str(annotation.user_id),
                        "annotation_type": annotation.annotation_type,
                        "content": annotation.content,
                        "is_resolved": annotation.is_resolved,
                        "updated_at": annotation.updated_at.isoformat()
                    },
                    "timestamp": datetime.utcnow().isoformat()
                },
                str(annotation.session_id),
                exclude_user=str(current_user.id)
            )
        
        return DocumentAnnotationResponse(
            id=annotation.id,
            session_id=annotation.session_id,
            user_id=annotation.user_id,
            annotation_type=annotation.annotation_type,
            content=annotation.content,
            page_number=annotation.page_number,
            start_offset=annotation.start_offset,
            end_offset=annotation.end_offset,
            selected_text=annotation.selected_text,
            style_data=annotation.style_data,
            annotation_metadata=annotation.annotation_metadata,
            is_resolved=annotation.is_resolved,
            resolved_by=annotation.resolved_by,
            resolved_at=annotation.resolved_at,
            created_at=annotation.created_at,
            updated_at=annotation.updated_at
        )
        
    except Exception as e:
        logger.error(f"Failed to update annotation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/annotations/{annotation_id}")
async def delete_annotation(
    annotation_id: uuid.UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an annotation."""
    try:
        collaboration_service = CollaborationService(db)
        
        # Get annotation details before deletion for WebSocket broadcast
        from app.database.models.collaboration import DocumentAnnotation
        annotation = db.query(DocumentAnnotation).filter(
            DocumentAnnotation.id == annotation_id
        ).first()
        
        if not annotation:
            raise HTTPException(status_code=404, detail="Annotation not found")
        
        session_id = annotation.session_id
        
        success = await collaboration_service.delete_annotation(annotation_id, current_user.id)
        
        if success:
            # Broadcast to WebSocket clients
            await connection_manager.broadcast_to_document_session(
                {
                    "type": "annotation_deleted",
                    "session_id": str(session_id),
                    "annotation_id": str(annotation_id),
                    "user_id": str(current_user.id),
                    "timestamp": datetime.utcnow().isoformat()
                },
                str(session_id),
                exclude_user=str(current_user.id)
            )
        
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Failed to delete annotation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/annotations", response_model=List[DocumentAnnotationResponse])
async def get_session_annotations(
    session_id: uuid.UUID,
    page_number: Optional[int] = Query(None, description="Filter by page number"),
    annotation_type: Optional[str] = Query(None, description="Filter by annotation type"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get annotations for a collaboration session."""
    try:
        collaboration_service = CollaborationService(db)
        
        annotations = await collaboration_service.get_session_annotations(
            session_id, page_number, annotation_type
        )
        
        annotation_responses = []
        for a in annotations:
            annotation_responses.append(DocumentAnnotationResponse(
                id=a.id,
                session_id=a.session_id,
                user_id=a.user_id,
                annotation_type=a.annotation_type,
                content=a.content,
                page_number=a.page_number,
                start_offset=a.start_offset,
                end_offset=a.end_offset,
                selected_text=a.selected_text,
                style_data=a.style_data,
                annotation_metadata=a.annotation_metadata,
                is_resolved=a.is_resolved,
                resolved_by=a.resolved_by,
                resolved_at=a.resolved_at,
                created_at=a.created_at,
                updated_at=a.updated_at
            ))
        
        return annotation_responses
        
    except Exception as e:
        logger.error(f"Failed to get session annotations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Conflict Resolution Endpoints

@router.post("/sessions/{session_id}/resolve-conflicts")
async def resolve_annotation_conflicts(
    session_id: uuid.UUID,
    conflict_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve conflicts between overlapping annotations."""
    try:
        collaboration_service = CollaborationService(db)
        
        conflicting_annotations = [
            uuid.UUID(aid) for aid in conflict_data.get("conflicting_annotations", [])
        ]
        resolution_strategy = conflict_data.get("resolution_strategy", "manual")
        
        success = await collaboration_service.resolve_annotation_conflict(
            session_id, conflicting_annotations, resolution_strategy, current_user.id
        )
        
        if success:
            # Broadcast conflict resolution to WebSocket clients
            await connection_manager.broadcast_to_document_session(
                {
                    "type": "conflict_resolved",
                    "session_id": str(session_id),
                    "conflicting_annotations": [str(aid) for aid in conflicting_annotations],
                    "resolution_strategy": resolution_strategy,
                    "resolved_by": str(current_user.id),
                    "timestamp": datetime.utcnow().isoformat()
                },
                str(session_id)
            )
        
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Failed to resolve annotation conflicts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Sync and Recovery Endpoints

@router.get("/sessions/{session_id}/events", response_model=List[CollaborationEventResponse])
async def get_session_events(
    session_id: uuid.UUID,
    since: Optional[datetime] = Query(None, description="Get events since this timestamp"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get collaboration events for session synchronization."""
    try:
        collaboration_service = CollaborationService(db)
        
        if since:
            events = await collaboration_service.get_session_events_since(session_id, since)
        else:
            # Get recent events (last hour by default)
            from datetime import timedelta
            since = datetime.utcnow() - timedelta(hours=1)
            events = await collaboration_service.get_session_events_since(session_id, since)
        
        event_responses = []
        for event in events:
            event_responses.append(CollaborationEventResponse(
                id=event.id,
                session_id=event.session_id,
                user_id=event.user_id,
                event_type=event.event_type,
                event_data=event.event_data,
                timestamp=event.timestamp
            ))
        
        return event_responses
        
    except Exception as e:
        logger.error(f"Failed to get session events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup/inactive-participants")
async def cleanup_inactive_participants(
    timeout_minutes: int = Query(30, description="Timeout in minutes for inactive participants"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clean up inactive participants (admin only)."""
    try:
        # Check if user has admin privileges (you may want to implement proper role checking)
        if not hasattr(current_user, 'role') or current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        collaboration_service = CollaborationService(db)
        
        count = await collaboration_service.cleanup_inactive_participants(timeout_minutes)
        
        return {
            "success": True,
            "cleaned_up_participants": count,
            "timeout_minutes": timeout_minutes
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup inactive participants: {e}")
        raise HTTPException(status_code=500, detail=str(e))