"""Collaboration service for real-time document collaboration."""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import uuid

from app.database.models.collaboration import (
    DocumentSession,
    SessionParticipant,
    DocumentAnnotation,
    CollaborationEvent
)
from app.database.models.user import User
from app.database.models.document import Document
from app.schemas.collaboration import (
    DocumentSessionCreate,
    DocumentAnnotationCreate,
    DocumentAnnotationUpdate,
    CollaborationEventCreate,
    CursorPosition
)
from app.core.exceptions import NotFoundError, ValidationError, ConflictError

logger = logging.getLogger(__name__)


class CollaborationService:
    """Service for managing document collaboration features."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Document Session Management
    
    async def create_session(
        self, 
        session_data: DocumentSessionCreate, 
        user_id: uuid.UUID
    ) -> DocumentSession:
        """Create a new document collaboration session."""
        # Verify document exists and user has access
        document = self.db.query(Document).filter(Document.id == session_data.document_id).first()
        if not document:
            raise NotFoundError("Document not found")
        
        # Create session
        session = DocumentSession(
            document_id=session_data.document_id,
            name=session_data.name,
            created_by=user_id
        )
        
        self.db.add(session)
        self.db.flush()  # Get the session ID
        
        # Add creator as first participant
        participant = SessionParticipant(
            session_id=session.id,
            user_id=user_id,
            is_online=True
        )
        
        self.db.add(participant)
        
        # Log event
        event = CollaborationEvent(
            session_id=session.id,
            user_id=user_id,
            event_type="session_created",
            event_data={"session_name": session_data.name}
        )
        
        self.db.add(event)
        self.db.commit()
        
        logger.info(f"Created collaboration session {session.id} for document {session_data.document_id}")
        return session
    
    async def get_session(self, session_id: uuid.UUID) -> Optional[DocumentSession]:
        """Get a document session by ID."""
        return self.db.query(DocumentSession).filter(
            and_(
                DocumentSession.id == session_id,
                DocumentSession.is_active == True
            )
        ).first()
    
    async def get_document_sessions(self, document_id: uuid.UUID) -> List[DocumentSession]:
        """Get all active sessions for a document."""
        return self.db.query(DocumentSession).filter(
            and_(
                DocumentSession.document_id == document_id,
                DocumentSession.is_active == True
            )
        ).all()
    
    async def close_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Close a document session."""
        session = await self.get_session(session_id)
        if not session:
            raise NotFoundError("Session not found")
        
        if session.created_by != user_id:
            raise ValidationError("Only session creator can close the session")
        
        session.is_active = False
        
        # Mark all participants as offline
        self.db.query(SessionParticipant).filter(
            SessionParticipant.session_id == session_id
        ).update({"is_online": False, "left_at": datetime.utcnow()})
        
        # Log event
        event = CollaborationEvent(
            session_id=session_id,
            user_id=user_id,
            event_type="session_closed"
        )
        
        self.db.add(event)
        self.db.commit()
        
        logger.info(f"Closed collaboration session {session_id}")
        return True
    
    # Participant Management
    
    async def join_session(
        self, 
        session_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> SessionParticipant:
        """Join a user to a collaboration session."""
        session = await self.get_session(session_id)
        if not session:
            raise NotFoundError("Session not found")
        
        # Check if user is already a participant
        existing_participant = self.db.query(SessionParticipant).filter(
            and_(
                SessionParticipant.session_id == session_id,
                SessionParticipant.user_id == user_id
            )
        ).first()
        
        if existing_participant:
            # Rejoin existing participant
            existing_participant.is_online = True
            existing_participant.last_seen = datetime.utcnow()
            existing_participant.left_at = None
            participant = existing_participant
        else:
            # Create new participant
            participant = SessionParticipant(
                session_id=session_id,
                user_id=user_id,
                is_online=True
            )
            self.db.add(participant)
        
        # Log event
        event = CollaborationEvent(
            session_id=session_id,
            user_id=user_id,
            event_type="user_joined"
        )
        
        self.db.add(event)
        self.db.commit()
        
        logger.info(f"User {user_id} joined session {session_id}")
        return participant
    
    async def leave_session(
        self, 
        session_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> bool:
        """Remove a user from a collaboration session."""
        participant = self.db.query(SessionParticipant).filter(
            and_(
                SessionParticipant.session_id == session_id,
                SessionParticipant.user_id == user_id
            )
        ).first()
        
        if not participant:
            return False
        
        participant.is_online = False
        participant.left_at = datetime.utcnow()
        
        # Log event
        event = CollaborationEvent(
            session_id=session_id,
            user_id=user_id,
            event_type="user_left"
        )
        
        self.db.add(event)
        self.db.commit()
        
        logger.info(f"User {user_id} left session {session_id}")
        return True
    
    async def update_user_presence(
        self, 
        session_id: uuid.UUID, 
        user_id: uuid.UUID,
        cursor_position: Optional[CursorPosition] = None
    ) -> bool:
        """Update user presence and cursor position."""
        participant = self.db.query(SessionParticipant).filter(
            and_(
                SessionParticipant.session_id == session_id,
                SessionParticipant.user_id == user_id
            )
        ).first()
        
        if not participant:
            return False
        
        participant.last_seen = datetime.utcnow()
        if cursor_position:
            participant.cursor_position = cursor_position.dict()
        
        self.db.commit()
        return True
    
    async def get_session_participants(
        self, 
        session_id: uuid.UUID,
        online_only: bool = False
    ) -> List[SessionParticipant]:
        """Get participants in a session."""
        query = self.db.query(SessionParticipant).filter(
            SessionParticipant.session_id == session_id
        )
        
        if online_only:
            query = query.filter(SessionParticipant.is_online == True)
        
        return query.all()
    
    # Annotation Management
    
    async def create_annotation(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        annotation_data: DocumentAnnotationCreate
    ) -> DocumentAnnotation:
        """Create a new document annotation."""
        session = await self.get_session(session_id)
        if not session:
            raise NotFoundError("Session not found")
        
        # Check for overlapping annotations (conflict detection)
        if annotation_data.start_offset is not None and annotation_data.end_offset is not None:
            overlapping = await self._check_annotation_overlap(
                session_id, 
                annotation_data.page_number,
                annotation_data.start_offset,
                annotation_data.end_offset
            )
            
            if overlapping:
                logger.warning(f"Overlapping annotation detected for user {user_id} in session {session_id}")
        
        annotation = DocumentAnnotation(
            session_id=session_id,
            user_id=user_id,
            annotation_type=annotation_data.annotation_type,
            content=annotation_data.content,
            page_number=annotation_data.page_number,
            start_offset=annotation_data.start_offset,
            end_offset=annotation_data.end_offset,
            selected_text=annotation_data.selected_text,
            style_data=annotation_data.style_data.dict() if annotation_data.style_data else None,
            annotation_metadata=annotation_data.annotation_metadata
        )
        
        self.db.add(annotation)
        self.db.flush()  # Get the annotation ID
        
        # Log event
        event = CollaborationEvent(
            session_id=session_id,
            user_id=user_id,
            event_type="annotation_created",
            event_data={
                "annotation_id": str(annotation.id),
                "annotation_type": annotation_data.annotation_type
            }
        )
        
        self.db.add(event)
        self.db.commit()
        
        logger.info(f"Created annotation {annotation.id} in session {session_id}")
        return annotation
    
    async def update_annotation(
        self,
        annotation_id: uuid.UUID,
        user_id: uuid.UUID,
        update_data: DocumentAnnotationUpdate
    ) -> Optional[DocumentAnnotation]:
        """Update an existing annotation."""
        annotation = self.db.query(DocumentAnnotation).filter(
            DocumentAnnotation.id == annotation_id
        ).first()
        
        if not annotation:
            raise NotFoundError("Annotation not found")
        
        if annotation.user_id != user_id:
            raise ValidationError("Can only update your own annotations")
        
        # Update fields
        if update_data.content is not None:
            annotation.content = update_data.content
        if update_data.style_data is not None:
            annotation.style_data = update_data.style_data.dict()
        if update_data.annotation_metadata is not None:
            annotation.annotation_metadata = update_data.annotation_metadata
        if update_data.is_resolved is not None:
            annotation.is_resolved = update_data.is_resolved
            if update_data.is_resolved:
                annotation.resolved_by = user_id
                annotation.resolved_at = datetime.utcnow()
        
        # Log event
        event = CollaborationEvent(
            session_id=annotation.session_id,
            user_id=user_id,
            event_type="annotation_updated",
            event_data={"annotation_id": str(annotation_id)}
        )
        
        self.db.add(event)
        self.db.commit()
        
        logger.info(f"Updated annotation {annotation_id}")
        return annotation
    
    async def delete_annotation(
        self,
        annotation_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Delete an annotation."""
        annotation = self.db.query(DocumentAnnotation).filter(
            DocumentAnnotation.id == annotation_id
        ).first()
        
        if not annotation:
            raise NotFoundError("Annotation not found")
        
        if annotation.user_id != user_id:
            raise ValidationError("Can only delete your own annotations")
        
        session_id = annotation.session_id
        
        self.db.delete(annotation)
        
        # Log event
        event = CollaborationEvent(
            session_id=session_id,
            user_id=user_id,
            event_type="annotation_deleted",
            event_data={"annotation_id": str(annotation_id)}
        )
        
        self.db.add(event)
        self.db.commit()
        
        logger.info(f"Deleted annotation {annotation_id}")
        return True
    
    async def get_session_annotations(
        self,
        session_id: uuid.UUID,
        page_number: Optional[int] = None,
        annotation_type: Optional[str] = None
    ) -> List[DocumentAnnotation]:
        """Get annotations for a session."""
        query = self.db.query(DocumentAnnotation).filter(
            DocumentAnnotation.session_id == session_id
        )
        
        if page_number is not None:
            query = query.filter(DocumentAnnotation.page_number == page_number)
        
        if annotation_type:
            query = query.filter(DocumentAnnotation.annotation_type == annotation_type)
        
        return query.order_by(DocumentAnnotation.created_at).all()
    
    # Conflict Resolution
    
    async def _check_annotation_overlap(
        self,
        session_id: uuid.UUID,
        page_number: Optional[int],
        start_offset: int,
        end_offset: int
    ) -> List[DocumentAnnotation]:
        """Check for overlapping annotations."""
        query = self.db.query(DocumentAnnotation).filter(
            and_(
                DocumentAnnotation.session_id == session_id,
                DocumentAnnotation.page_number == page_number,
                or_(
                    and_(
                        DocumentAnnotation.start_offset <= start_offset,
                        DocumentAnnotation.end_offset >= start_offset
                    ),
                    and_(
                        DocumentAnnotation.start_offset <= end_offset,
                        DocumentAnnotation.end_offset >= end_offset
                    ),
                    and_(
                        DocumentAnnotation.start_offset >= start_offset,
                        DocumentAnnotation.end_offset <= end_offset
                    )
                )
            )
        )
        
        return query.all()
    
    async def resolve_annotation_conflict(
        self,
        session_id: uuid.UUID,
        conflicting_annotations: List[uuid.UUID],
        resolution_strategy: str,
        user_id: uuid.UUID
    ) -> bool:
        """Resolve conflicts between overlapping annotations."""
        if resolution_strategy == "merge":
            # Merge overlapping annotations
            return await self._merge_annotations(conflicting_annotations, user_id)
        elif resolution_strategy == "override":
            # Keep the latest annotation, remove others
            return await self._override_annotations(conflicting_annotations, user_id)
        else:
            # Manual resolution - just log the conflict
            event = CollaborationEvent(
                session_id=session_id,
                user_id=user_id,
                event_type="conflict_manual_resolution",
                event_data={
                    "conflicting_annotations": [str(aid) for aid in conflicting_annotations],
                    "strategy": resolution_strategy
                }
            )
            self.db.add(event)
            self.db.commit()
            return True
    
    async def _merge_annotations(
        self,
        annotation_ids: List[uuid.UUID],
        user_id: uuid.UUID
    ) -> bool:
        """Merge multiple annotations into one."""
        annotations = self.db.query(DocumentAnnotation).filter(
            DocumentAnnotation.id.in_(annotation_ids)
        ).all()
        
        if len(annotations) < 2:
            return False
        
        # Find the bounds of all annotations
        min_start = min(a.start_offset for a in annotations if a.start_offset is not None)
        max_end = max(a.end_offset for a in annotations if a.end_offset is not None)
        
        # Merge content
        merged_content = " | ".join(a.content for a in annotations if a.content)
        
        # Keep the first annotation, update its bounds and content
        primary_annotation = annotations[0]
        primary_annotation.start_offset = min_start
        primary_annotation.end_offset = max_end
        primary_annotation.content = merged_content
        
        # Delete other annotations
        for annotation in annotations[1:]:
            self.db.delete(annotation)
        
        self.db.commit()
        return True
    
    async def _override_annotations(
        self,
        annotation_ids: List[uuid.UUID],
        user_id: uuid.UUID
    ) -> bool:
        """Keep the latest annotation, remove others."""
        annotations = self.db.query(DocumentAnnotation).filter(
            DocumentAnnotation.id.in_(annotation_ids)
        ).order_by(desc(DocumentAnnotation.created_at)).all()
        
        if len(annotations) < 2:
            return False
        
        # Keep the first (latest) annotation, delete others
        for annotation in annotations[1:]:
            self.db.delete(annotation)
        
        self.db.commit()
        return True
    
    # Sync and Recovery
    
    async def get_session_events_since(
        self,
        session_id: uuid.UUID,
        since_timestamp: datetime
    ) -> List[CollaborationEvent]:
        """Get collaboration events since a specific timestamp for sync."""
        return self.db.query(CollaborationEvent).filter(
            and_(
                CollaborationEvent.session_id == session_id,
                CollaborationEvent.timestamp > since_timestamp
            )
        ).order_by(CollaborationEvent.timestamp).all()
    
    async def cleanup_inactive_participants(self, timeout_minutes: int = 30):
        """Clean up participants who haven't been seen for a while."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        
        inactive_participants = self.db.query(SessionParticipant).filter(
            and_(
                SessionParticipant.is_online == True,
                SessionParticipant.last_seen < cutoff_time
            )
        ).all()
        
        for participant in inactive_participants:
            participant.is_online = False
            participant.left_at = datetime.utcnow()
            
            # Log event
            event = CollaborationEvent(
                session_id=participant.session_id,
                user_id=participant.user_id,
                event_type="user_timeout"
            )
            self.db.add(event)
        
        if inactive_participants:
            self.db.commit()
            logger.info(f"Cleaned up {len(inactive_participants)} inactive participants")
        
        return len(inactive_participants)