"""Conversation memory management for maintaining context in AI interactions."""

import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum


class MessageRole(str, Enum):
    """Message roles in conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ConversationMessage:
    """Represents a single message in a conversation."""
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    token_count: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage':
        """Create message from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['role'] = MessageRole(data['role'])
        return cls(**data)


@dataclass
class ConversationSession:
    """Represents a conversation session with metadata."""
    session_id: str
    document_id: Optional[str]
    user_id: str
    jurisdiction: Optional[str]
    created_at: datetime
    last_activity: datetime
    messages: List[ConversationMessage]
    context_metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary format."""
        return {
            'session_id': self.session_id,
            'document_id': self.document_id,
            'user_id': self.user_id,
            'jurisdiction': self.jurisdiction,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'messages': [msg.to_dict() for msg in self.messages],
            'context_metadata': self.context_metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationSession':
        """Create session from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        data['messages'] = [ConversationMessage.from_dict(msg) for msg in data['messages']]
        return cls(**data)


class ConversationMemoryManager:
    """Manages conversation memory with context-aware truncation and retrieval."""
    
    def __init__(
        self,
        max_tokens: int = 8000,
        max_messages: int = 50,
        context_window_messages: int = 10,
        session_timeout_hours: int = 24
    ):
        """
        Initialize conversation memory manager.
        
        Args:
            max_tokens: Maximum tokens to keep in memory
            max_messages: Maximum number of messages to keep
            context_window_messages: Number of recent messages to always include
            session_timeout_hours: Hours after which sessions expire
        """
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.context_window_messages = context_window_messages
        self.session_timeout = timedelta(hours=session_timeout_hours)
        
        # In-memory storage (in production, use Redis or database)
        self._sessions: Dict[str, ConversationSession] = {}
    
    def create_session(
        self,
        session_id: str,
        user_id: str,
        document_id: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        context_metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationSession:
        """Create a new conversation session."""
        now = datetime.utcnow()
        
        session = ConversationSession(
            session_id=session_id,
            document_id=document_id,
            user_id=user_id,
            jurisdiction=jurisdiction,
            created_at=now,
            last_activity=now,
            messages=[],
            context_metadata=context_metadata or {}
        )
        
        self._sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get an existing conversation session."""
        session = self._sessions.get(session_id)
        
        if session and self._is_session_expired(session):
            self.delete_session(session_id)
            return None
        
        return session
    
    def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        token_count: Optional[int] = None
    ) -> bool:
        """Add a message to the conversation session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata,
            token_count=token_count
        )
        
        session.messages.append(message)
        session.last_activity = datetime.utcnow()
        
        # Truncate if necessary
        self._truncate_session(session)
        
        return True
    
    def get_conversation_history(
        self,
        session_id: str,
        include_system: bool = True,
        max_messages: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for OpenAI API.
        
        Args:
            session_id: Session identifier
            include_system: Whether to include system messages
            max_messages: Maximum number of messages to return
            
        Returns:
            List of messages in OpenAI format
        """
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = session.messages
        
        if not include_system:
            messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
        
        if max_messages:
            messages = messages[-max_messages:]
        
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]
    
    def get_context_summary(self, session_id: str) -> Optional[str]:
        """Get a summary of the conversation context."""
        session = self.get_session(session_id)
        if not session or not session.messages:
            return None
        
        # Get recent user messages for context
        recent_messages = [
            msg for msg in session.messages[-self.context_window_messages:]
            if msg.role == MessageRole.USER
        ]
        
        if not recent_messages:
            return None
        
        context_parts = []
        
        # Add document context if available
        if session.document_id:
            context_parts.append(f"Document ID: {session.document_id}")
        
        if session.jurisdiction:
            context_parts.append(f"Jurisdiction: {session.jurisdiction}")
        
        # Add recent topics
        topics = [msg.content[:100] + "..." if len(msg.content) > 100 else msg.content 
                 for msg in recent_messages[-3:]]
        
        if topics:
            context_parts.append(f"Recent topics: {'; '.join(topics)}")
        
        return " | ".join(context_parts)
    
    def update_session_metadata(
        self,
        session_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Update session metadata."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        if session.context_metadata is None:
            session.context_metadata = {}
        
        session.context_metadata.update(metadata)
        session.last_activity = datetime.utcnow()
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a conversation session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of deleted sessions."""
        expired_sessions = [
            session_id for session_id, session in self._sessions.items()
            if self._is_session_expired(session)
        ]
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
        
        return len(expired_sessions)
    
    def get_session_statistics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics about a conversation session."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        total_tokens = sum(
            msg.token_count for msg in session.messages 
            if msg.token_count is not None
        )
        
        message_counts = {}
        for msg in session.messages:
            role = msg.role.value
            message_counts[role] = message_counts.get(role, 0) + 1
        
        return {
            'session_id': session_id,
            'total_messages': len(session.messages),
            'total_tokens': total_tokens,
            'message_counts': message_counts,
            'duration_hours': (session.last_activity - session.created_at).total_seconds() / 3600,
            'document_id': session.document_id,
            'jurisdiction': session.jurisdiction
        }
    
    def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session data for backup or analysis."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return session.to_dict()
    
    def import_session(self, session_data: Dict[str, Any]) -> bool:
        """Import session data from backup."""
        try:
            session = ConversationSession.from_dict(session_data)
            self._sessions[session.session_id] = session
            return True
        except Exception:
            return False
    
    def _is_session_expired(self, session: ConversationSession) -> bool:
        """Check if a session has expired."""
        return datetime.utcnow() - session.last_activity > self.session_timeout
    
    def _truncate_session(self, session: ConversationSession) -> None:
        """Truncate session messages to stay within limits."""
        # First, remove old messages if we exceed max_messages
        if len(session.messages) > self.max_messages:
            # Keep system messages and recent messages
            system_messages = [msg for msg in session.messages if msg.role == MessageRole.SYSTEM]
            recent_messages = [msg for msg in session.messages[-self.context_window_messages:] 
                             if msg.role != MessageRole.SYSTEM]
            
            session.messages = system_messages + recent_messages
        
        # Then, truncate by token count if necessary
        if self.max_tokens > 0:
            total_tokens = sum(
                msg.token_count for msg in session.messages 
                if msg.token_count is not None
            )
            
            while total_tokens > self.max_tokens and len(session.messages) > self.context_window_messages:
                # Remove oldest non-system message
                for i, msg in enumerate(session.messages):
                    if msg.role != MessageRole.SYSTEM:
                        removed_msg = session.messages.pop(i)
                        if removed_msg.token_count:
                            total_tokens -= removed_msg.token_count
                        break
                else:
                    # No more non-system messages to remove
                    break
    
    def get_all_sessions(self, user_id: Optional[str] = None) -> List[str]:
        """Get all session IDs, optionally filtered by user."""
        if user_id:
            return [
                session_id for session_id, session in self._sessions.items()
                if session.user_id == user_id and not self._is_session_expired(session)
            ]
        else:
            return [
                session_id for session_id, session in self._sessions.items()
                if not self._is_session_expired(session)
            ]