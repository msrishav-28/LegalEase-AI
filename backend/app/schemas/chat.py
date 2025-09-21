"""Chat-related Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    """Schema for creating a new chat session."""
    title: Optional[str] = Field(None, description="Session title")
    document_id: Optional[str] = Field(None, description="Associated document ID")
    jurisdiction: Optional[str] = Field(None, description="Legal jurisdiction context")


class ChatSessionResponse(BaseModel):
    """Schema for chat session response."""
    id: str = Field(..., description="Session ID")
    title: str = Field(..., description="Session title")
    document_id: Optional[str] = Field(None, description="Associated document ID")
    jurisdiction: Optional[str] = Field(None, description="Legal jurisdiction")
    message_count: int = Field(..., description="Number of messages in session")
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(..., description="Whether session is active")


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message."""
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction context for this message")


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""
    id: str = Field(..., description="Message ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction context")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence score")
    references: Optional[List[Dict[str, Any]]] = Field(None, description="Document references")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ChatStreamRequest(BaseModel):
    """Schema for streaming chat request."""
    message: str = Field(..., min_length=1, max_length=10000, description="Message to stream")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction context")


class DocumentReference(BaseModel):
    """Schema for document reference in chat."""
    document_id: str = Field(..., description="Referenced document ID")
    document_name: str = Field(..., description="Document name")
    section: Optional[str] = Field(None, description="Referenced section")
    page_number: Optional[int] = Field(None, description="Page number")
    relevance: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    excerpt: str = Field(..., description="Relevant text excerpt")
    jurisdiction: Optional[str] = Field(None, description="Document jurisdiction")


class JurisdictionBadge(BaseModel):
    """Schema for jurisdiction badge information."""
    jurisdiction: str = Field(..., description="Jurisdiction identifier")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    color: str = Field(..., description="Badge color")
    label: str = Field(..., description="Display label")


class ChatSuggestion(BaseModel):
    """Schema for chat suggestions."""
    text: str = Field(..., description="Suggestion text")
    type: str = Field(..., description="Suggestion type")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction context")
    description: Optional[str] = Field(None, description="Suggestion description")
    category: str = Field(..., description="Suggestion category")


class JurisdictionContextResponse(BaseModel):
    """Schema for jurisdiction context response."""
    jurisdiction: Optional[str] = Field(None, description="Detected jurisdiction")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    suggestions: List[str] = Field(..., description="Jurisdiction-specific suggestions")
    applicable_laws: List[str] = Field(..., description="Applicable laws and regulations")
    compliance_requirements: List[str] = Field(..., description="Compliance requirements")
    document_type: Optional[str] = Field(None, description="Document type")
    document_name: Optional[str] = Field(None, description="Document name")


class ChatAutoCompleteResponse(BaseModel):
    """Schema for chat auto-complete response."""
    suggestions: List[ChatSuggestion] = Field(..., description="Auto-complete suggestions")
    jurisdiction: Optional[str] = Field(None, description="Current jurisdiction context")


class TypingIndicator(BaseModel):
    """Schema for typing indicator."""
    user_id: str = Field(..., description="User ID")
    user_name: str = Field(..., description="User name")
    is_typing: bool = Field(..., description="Whether user is typing")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction context")


class ChatAnalyticsResponse(BaseModel):
    """Schema for chat analytics."""
    session_id: str = Field(..., description="Session ID")
    total_messages: int = Field(..., description="Total messages in session")
    user_messages: int = Field(..., description="User messages count")
    ai_messages: int = Field(..., description="AI messages count")
    average_response_time: float = Field(..., description="Average AI response time")
    jurisdiction_distribution: Dict[str, int] = Field(..., description="Jurisdiction usage distribution")
    most_common_topics: List[str] = Field(..., description="Most discussed topics")
    session_duration: float = Field(..., description="Session duration in minutes")


class ChatExportRequest(BaseModel):
    """Schema for chat export request."""
    session_id: str = Field(..., description="Session ID to export")
    format: str = Field(..., description="Export format (json, pdf, txt)")
    include_metadata: bool = Field(True, description="Include message metadata")
    include_references: bool = Field(True, description="Include document references")


class ChatExportResponse(BaseModel):
    """Schema for chat export response."""
    export_id: str = Field(..., description="Export ID")
    download_url: str = Field(..., description="Download URL")
    format: str = Field(..., description="Export format")
    file_size: int = Field(..., description="File size in bytes")
    expires_at: datetime = Field(..., description="Download link expiration")


class ChatFeedback(BaseModel):
    """Schema for chat message feedback."""
    message_id: str = Field(..., description="Message ID")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    feedback_type: str = Field(..., description="Feedback type (helpful, accurate, etc.)")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional comment")


class ChatSettings(BaseModel):
    """Schema for user chat settings."""
    default_jurisdiction: Optional[str] = Field(None, description="Default jurisdiction")
    auto_detect_jurisdiction: bool = Field(True, description="Auto-detect jurisdiction")
    show_confidence_scores: bool = Field(True, description="Show AI confidence scores")
    enable_streaming: bool = Field(True, description="Enable streaming responses")
    max_context_messages: int = Field(10, ge=1, le=50, description="Max context messages")
    preferred_response_style: str = Field("detailed", description="Response style preference")


class ChatHealthCheck(BaseModel):
    """Schema for chat service health check."""
    status: str = Field(..., description="Service status")
    ai_service_available: bool = Field(..., description="AI service availability")
    jurisdiction_detection_available: bool = Field(..., description="Jurisdiction detection availability")
    streaming_available: bool = Field(..., description="Streaming capability")
    active_sessions: int = Field(..., description="Number of active sessions")
    average_response_time: float = Field(..., description="Average response time in seconds")
    last_check: datetime = Field(..., description="Last health check timestamp")


# WebSocket message schemas
class WebSocketMessage(BaseModel):
    """Base schema for WebSocket messages."""
    type: str = Field(..., description="Message type")
    payload: Dict[str, Any] = Field(..., description="Message payload")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")


class ChatWebSocketMessage(WebSocketMessage):
    """Schema for chat WebSocket messages."""
    session_id: str = Field(..., description="Chat session ID")
    user_id: str = Field(..., description="User ID")


class TypingWebSocketMessage(ChatWebSocketMessage):
    """Schema for typing indicator WebSocket messages."""
    type: str = Field("typing", description="Message type")
    is_typing: bool = Field(..., description="Typing status")


class MessageWebSocketMessage(ChatWebSocketMessage):
    """Schema for chat message WebSocket messages."""
    type: str = Field("message", description="Message type")
    message: ChatMessageResponse = Field(..., description="Chat message")


class JurisdictionUpdateWebSocketMessage(ChatWebSocketMessage):
    """Schema for jurisdiction update WebSocket messages."""
    type: str = Field("jurisdiction_update", description="Message type")
    jurisdiction: str = Field(..., description="Updated jurisdiction")
    confidence: float = Field(..., description="Detection confidence")


class ErrorWebSocketMessage(WebSocketMessage):
    """Schema for error WebSocket messages."""
    type: str = Field("error", description="Message type")
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")


# Configuration schemas
class ChatConfiguration(BaseModel):
    """Schema for chat service configuration."""
    max_sessions_per_user: int = Field(10, description="Maximum sessions per user")
    max_messages_per_session: int = Field(1000, description="Maximum messages per session")
    session_timeout_minutes: int = Field(60, description="Session timeout in minutes")
    enable_analytics: bool = Field(True, description="Enable chat analytics")
    enable_feedback: bool = Field(True, description="Enable message feedback")
    supported_jurisdictions: List[str] = Field(
        ["india", "usa", "cross_border"],
        description="Supported jurisdictions"
    )
    ai_model_config: Dict[str, Any] = Field(
        {
            "model": "gpt-4-turbo-preview",
            "temperature": 0.1,
            "max_tokens": 4000
        },
        description="AI model configuration"
    )