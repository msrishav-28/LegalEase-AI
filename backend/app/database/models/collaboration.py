"""Collaboration models for real-time document collaboration."""

from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import func
import uuid
from typing import Dict, Any, Optional

from .base import BaseModel


class DocumentSession(BaseModel):
    """Document collaboration session model."""
    
    __tablename__ = "document_sessions"
    
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)  # Session name
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="sessions")
    creator = relationship("User", foreign_keys=[created_by])
    participants = relationship("SessionParticipant", back_populates="session", cascade="all, delete-orphan")
    annotations = relationship("DocumentAnnotation", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<DocumentSession(id={self.id}, document_id={self.document_id}, name={self.name})>"


class SessionParticipant(BaseModel):
    """Participant in a document collaboration session."""
    
    __tablename__ = "session_participants"
    
    session_id = Column(UUID(as_uuid=True), ForeignKey("document_sessions.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    left_at = Column(DateTime(timezone=True), nullable=True)
    is_online = Column(Boolean, default=True, nullable=False)
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    cursor_position = Column(JSON, nullable=True)  # Store cursor position data
    
    # Relationships
    session = relationship("DocumentSession", back_populates="participants")
    user = relationship("User")
    
    def __repr__(self) -> str:
        return f"<SessionParticipant(session_id={self.session_id}, user_id={self.user_id}, is_online={self.is_online})>"


class DocumentAnnotation(BaseModel):
    """Document annotation model for collaborative annotations."""
    
    __tablename__ = "document_annotations"
    
    session_id = Column(UUID(as_uuid=True), ForeignKey("document_sessions.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    annotation_type = Column(String(50), nullable=False)  # 'highlight', 'comment', 'note'
    content = Column(Text, nullable=True)  # Annotation content/comment
    
    # Position data
    page_number = Column(Integer, nullable=True)
    start_offset = Column(Integer, nullable=True)
    end_offset = Column(Integer, nullable=True)
    selected_text = Column(Text, nullable=True)
    
    # Styling and metadata
    style_data = Column(JSON, nullable=True)  # Color, font, etc.
    annotation_metadata = Column(JSON, nullable=True)  # Additional metadata
    
    # Status
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    session = relationship("DocumentSession", back_populates="annotations")
    user = relationship("User", foreign_keys=[user_id])
    resolver = relationship("User", foreign_keys=[resolved_by])
    
    def __repr__(self) -> str:
        return f"<DocumentAnnotation(id={self.id}, type={self.annotation_type}, user_id={self.user_id})>"


class CollaborationEvent(BaseModel):
    """Event log for collaboration activities."""
    
    __tablename__ = "collaboration_events"
    
    session_id = Column(UUID(as_uuid=True), ForeignKey("document_sessions.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # 'join', 'leave', 'annotate', 'cursor_move'
    event_data = Column(JSON, nullable=True)  # Event-specific data
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("DocumentSession")
    user = relationship("User")
    
    def __repr__(self) -> str:
        return f"<CollaborationEvent(type={self.event_type}, user_id={self.user_id}, timestamp={self.timestamp})>"