"""WebSocket endpoints for real-time chat functionality."""

import asyncio
import json
import logging
from typing import Dict, Set, Optional
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.websockets import WebSocketState

from app.services.user_service import get_current_user_websocket
from app.services.ai_analysis_service import AIAnalysisService
from app.schemas.user import User
from app.schemas.chat import (
    WebSocketMessage,
    TypingWebSocketMessage,
    MessageWebSocketMessage,
    JurisdictionUpdateWebSocketMessage,
    ErrorWebSocketMessage
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws/chat", tags=["chat-websocket"])


class ChatWebSocketManager:
    """Manages WebSocket connections for chat sessions."""
    
    def __init__(self):
        # Active connections: session_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # User sessions: user_id -> set of session_ids
        self.user_sessions: Dict[str, Set[str]] = {}
        # WebSocket to user mapping
        self.websocket_users: Dict[WebSocket, str] = {}
        # Typing indicators: session_id -> set of user_ids
        self.typing_users: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Connect a WebSocket to a chat session."""
        await websocket.accept()
        
        # Add to active connections
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        
        # Track user sessions
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(session_id)
        
        # Map websocket to user
        self.websocket_users[websocket] = user_id
        
        logger.info(f"User {user_id} connected to chat session {session_id}")
        
        # Notify other users in the session
        await self.broadcast_to_session(
            session_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_websocket=websocket
        )
    
    async def disconnect(self, websocket: WebSocket, session_id: str):
        """Disconnect a WebSocket from a chat session."""
        user_id = self.websocket_users.get(websocket)
        
        # Remove from active connections
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        # Remove from user sessions
        if user_id and user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]
        
        # Remove websocket mapping
        if websocket in self.websocket_users:
            del self.websocket_users[websocket]
        
        # Remove from typing indicators
        if session_id in self.typing_users and user_id:
            self.typing_users[session_id].discard(user_id)
        
        if user_id:
            logger.info(f"User {user_id} disconnected from chat session {session_id}")
            
            # Notify other users in the session
            await self.broadcast_to_session(
                session_id,
                {
                    "type": "user_left",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    async def broadcast_to_session(
        self,
        session_id: str,
        message: Dict,
        exclude_websocket: Optional[WebSocket] = None
    ):
        """Broadcast a message to all connections in a session."""
        if session_id not in self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected_websockets = set()
        
        for websocket in self.active_connections[session_id]:
            if websocket == exclude_websocket:
                continue
                
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(message_str)
                else:
                    disconnected_websockets.add(websocket)
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {str(e)}")
                disconnected_websockets.add(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected_websockets:
            await self.disconnect(websocket, session_id)
    
    async def send_to_user(self, user_id: str, message: Dict):
        """Send a message to all sessions of a specific user."""
        if user_id not in self.user_sessions:
            return
        
        for session_id in self.user_sessions[user_id]:
            await self.broadcast_to_session(session_id, message)
    
    async def handle_typing_indicator(
        self,
        session_id: str,
        user_id: str,
        is_typing: bool
    ):
        """Handle typing indicator updates."""
        if session_id not in self.typing_users:
            self.typing_users[session_id] = set()
        
        if is_typing:
            self.typing_users[session_id].add(user_id)
        else:
            self.typing_users[session_id].discard(user_id)
        
        # Broadcast typing status
        await self.broadcast_to_session(
            session_id,
            {
                "type": "typing_update",
                "user_id": user_id,
                "is_typing": is_typing,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def get_session_users(self, session_id: str) -> Set[str]:
        """Get all users currently in a session."""
        if session_id not in self.active_connections:
            return set()
        
        users = set()
        for websocket in self.active_connections[session_id]:
            user_id = self.websocket_users.get(websocket)
            if user_id:
                users.add(user_id)
        
        return users
    
    def get_typing_users(self, session_id: str) -> Set[str]:
        """Get users currently typing in a session."""
        return self.typing_users.get(session_id, set())


# Global WebSocket manager
websocket_manager = ChatWebSocketManager()
ai_service = AIAnalysisService()


@router.websocket("/{session_id}")
async def chat_websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    user: User = Depends(get_current_user_websocket)
):
    """WebSocket endpoint for real-time chat functionality."""
    try:
        await websocket_manager.connect(websocket, session_id, user.id)
        
        # Send initial session state
        await websocket.send_text(json.dumps({
            "type": "session_joined",
            "session_id": session_id,
            "user_id": user.id,
            "active_users": list(websocket_manager.get_session_users(session_id)),
            "typing_users": list(websocket_manager.get_typing_users(session_id)),
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await handle_websocket_message(
                    websocket, session_id, user.id, message
                )
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }))
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }))
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
    
    finally:
        await websocket_manager.disconnect(websocket, session_id)


async def handle_websocket_message(
    websocket: WebSocket,
    session_id: str,
    user_id: str,
    message: Dict
):
    """Handle incoming WebSocket messages."""
    message_type = message.get("type")
    
    if message_type == "typing":
        # Handle typing indicator
        is_typing = message.get("is_typing", False)
        await websocket_manager.handle_typing_indicator(
            session_id, user_id, is_typing
        )
    
    elif message_type == "chat_message":
        # Handle chat message
        content = message.get("content", "").strip()
        jurisdiction = message.get("jurisdiction")
        
        if not content:
            await websocket.send_text(json.dumps({
                "type": "error",
                "error": "Message content cannot be empty",
                "timestamp": datetime.utcnow().isoformat()
            }))
            return
        
        # Broadcast user message to other users
        await websocket_manager.broadcast_to_session(
            session_id,
            {
                "type": "user_message",
                "user_id": user_id,
                "content": content,
                "jurisdiction": jurisdiction,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_websocket=websocket
        )
        
        # Generate AI response (in background)
        asyncio.create_task(
            generate_ai_response(session_id, content, jurisdiction, user_id)
        )
    
    elif message_type == "jurisdiction_update":
        # Handle jurisdiction context update
        jurisdiction = message.get("jurisdiction")
        confidence = message.get("confidence", 0.0)
        
        await websocket_manager.broadcast_to_session(
            session_id,
            {
                "type": "jurisdiction_updated",
                "jurisdiction": jurisdiction,
                "confidence": confidence,
                "updated_by": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    elif message_type == "request_context":
        # Handle context request
        session_users = websocket_manager.get_session_users(session_id)
        typing_users = websocket_manager.get_typing_users(session_id)
        
        await websocket.send_text(json.dumps({
            "type": "session_context",
            "session_id": session_id,
            "active_users": list(session_users),
            "typing_users": list(typing_users),
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    else:
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": f"Unknown message type: {message_type}",
            "timestamp": datetime.utcnow().isoformat()
        }))


async def generate_ai_response(
    session_id: str,
    question: str,
    jurisdiction: Optional[str],
    user_id: str
):
    """Generate AI response and broadcast to session."""
    try:
        # Show typing indicator for AI
        await websocket_manager.broadcast_to_session(
            session_id,
            {
                "type": "ai_typing",
                "is_typing": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Generate AI response
        response = await ai_service.chat_with_document(
            session_id=session_id,
            question=question,
            user_id=user_id,
            jurisdiction=jurisdiction
        )
        
        # Stop typing indicator
        await websocket_manager.broadcast_to_session(
            session_id,
            {
                "type": "ai_typing",
                "is_typing": False,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Broadcast AI response
        await websocket_manager.broadcast_to_session(
            session_id,
            {
                "type": "ai_message",
                "content": response["response"],
                "confidence": response.get("metadata", {}).get("confidence"),
                "jurisdiction": jurisdiction,
                "references": response.get("parsed_response", {}).get("citations", []),
                "metadata": response.get("metadata", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        
        # Stop typing indicator
        await websocket_manager.broadcast_to_session(
            session_id,
            {
                "type": "ai_typing",
                "is_typing": False,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Send error message
        await websocket_manager.broadcast_to_session(
            session_id,
            {
                "type": "ai_error",
                "error": "Failed to generate AI response",
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.websocket("/health")
async def websocket_health_check(websocket: WebSocket):
    """WebSocket health check endpoint."""
    await websocket.accept()
    
    try:
        await websocket.send_text(json.dumps({
            "status": "healthy",
            "active_sessions": len(websocket_manager.active_connections),
            "total_connections": sum(
                len(connections) 
                for connections in websocket_manager.active_connections.values()
            ),
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Keep connection alive for monitoring
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat()
                }))
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket health check error: {str(e)}")
    finally:
        await websocket.close()


# Utility functions for external use
def get_websocket_manager() -> ChatWebSocketManager:
    """Get the global WebSocket manager instance."""
    return websocket_manager


async def notify_session_update(session_id: str, update_data: Dict):
    """Notify all users in a session about an update."""
    await websocket_manager.broadcast_to_session(session_id, update_data)


async def notify_user_update(user_id: str, update_data: Dict):
    """Notify a specific user about an update."""
    await websocket_manager.send_to_user(user_id, update_data)