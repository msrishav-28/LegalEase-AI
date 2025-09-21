"""Schemas for collaboration features."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class CursorPosition(BaseModel):
    """Cursor position data."""
    page: Optional[int] = None
    x: Optional[float] = None
    y: Optional[float] = None
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None


class AnnotationStyle(BaseModel):
    """Annotation styling data."""
    color: Optional[str] = "#ffff00"  # Default yellow
    opacity: Optional[float] = 0.3
    border_color: Optional[str] = None
    font_size: Optional[int] = None


class DocumentAnnotationCreate(BaseModel):
    """Schema for creating document annotations."""
    annotation_type: str = Field(..., description="Type of annotation (highlight, comment, note)")
    content: Optional[str] = Field(None, description="Annotation content/comment")
    page_number: Optional[int] = Field(None, description="Page number")
    start_offset: Optional[int] = Field(None, description="Start text offset")
    end_offset: Optional[int] = Field(None, description="End text offset")
    selected_text: Optional[str] = Field(None, description="Selected text content")
    style_data: Optional[AnnotationStyle] = Field(None, description="Styling information")
    annotation_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class DocumentAnnotationUpdate(BaseModel):
    """Schema for updating document annotations."""
    content: Optional[str] = None
    style_data: Optional[AnnotationStyle] = None
    annotation_metadata: Optional[Dict[str, Any]] = None
    is_resolved: Optional[bool] = None


class DocumentAnnotationResponse(BaseModel):
    """Schema for document annotation responses."""
    id: uuid.UUID
    session_id: uuid.UUID
    user_id: uuid.UUID
    annotation_type: str
    content: Optional[str]
    page_number: Optional[int]
    start_offset: Optional[int]
    end_offset: Optional[int]
    selected_text: Optional[str]
    style_data: Optional[Dict[str, Any]]
    annotation_metadata: Optional[Dict[str, Any]]
    is_resolved: bool
    resolved_by: Optional[uuid.UUID]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionParticipantResponse(BaseModel):
    """Schema for session participant responses."""
    id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    user_email: str
    joined_at: datetime
    left_at: Optional[datetime]
    is_online: bool
    last_seen: datetime
    cursor_position: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class DocumentSessionCreate(BaseModel):
    """Schema for creating document sessions."""
    document_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255, description="Session name")


class DocumentSessionResponse(BaseModel):
    """Schema for document session responses."""
    id: uuid.UUID
    document_id: uuid.UUID
    name: str
    is_active: bool
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    participants: List[SessionParticipantResponse] = []
    annotations: List[DocumentAnnotationResponse] = []

    class Config:
        from_attributes = True


class CollaborationEventCreate(BaseModel):
    """Schema for creating collaboration events."""
    event_type: str = Field(..., description="Event type (join, leave, annotate, cursor_move)")
    event_data: Optional[Dict[str, Any]] = Field(None, description="Event-specific data")


class CollaborationEventResponse(BaseModel):
    """Schema for collaboration event responses."""
    id: uuid.UUID
    session_id: uuid.UUID
    user_id: uuid.UUID
    event_type: str
    event_data: Optional[Dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True


# WebSocket message schemas
class WebSocketMessage(BaseModel):
    """Base WebSocket message schema."""
    type: str
    timestamp: Optional[datetime] = None


class JoinDocumentMessage(WebSocketMessage):
    """Join document session message."""
    type: str = "join_document"
    document_id: uuid.UUID
    session_id: Optional[uuid.UUID] = None


class LeaveDocumentMessage(WebSocketMessage):
    """Leave document session message."""
    type: str = "leave_document"
    document_id: uuid.UUID
    session_id: Optional[uuid.UUID] = None


class CursorUpdateMessage(WebSocketMessage):
    """Cursor position update message."""
    type: str = "cursor_position"
    document_id: uuid.UUID
    session_id: uuid.UUID
    position: CursorPosition


class AnnotationMessage(WebSocketMessage):
    """Annotation update message."""
    type: str = "document_annotation"
    document_id: uuid.UUID
    session_id: uuid.UUID
    annotation: DocumentAnnotationCreate
    action: str = Field(..., description="Action type (create, update, delete)")
    annotation_id: Optional[uuid.UUID] = None


class UserPresenceMessage(WebSocketMessage):
    """User presence notification message."""
    type: str = "user_presence"
    document_id: uuid.UUID
    session_id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    action: str = Field(..., description="Presence action (joined, left, online, offline)")


class ConflictResolutionMessage(WebSocketMessage):
    """Conflict resolution message."""
    type: str = "conflict_resolution"
    document_id: uuid.UUID
    session_id: uuid.UUID
    conflict_type: str = Field(..., description="Type of conflict (annotation_overlap, simultaneous_edit)")
    conflict_data: Dict[str, Any]
    resolution_strategy: str = Field(..., description="Resolution strategy (merge, override, manual)")


class SyncRequestMessage(WebSocketMessage):
    """Sync request message for reconnection."""
    type: str = "sync_request"
    document_id: uuid.UUID
    session_id: uuid.UUID
    last_sync_timestamp: Optional[datetime] = None