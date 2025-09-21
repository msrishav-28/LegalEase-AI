"""WebSocket endpoints for real-time communication."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.websockets import WebSocketState
from sqlalchemy.orm import Session
import uuid

from app.core.dependencies import get_current_user, get_db
from app.celery_app.monitoring import task_monitor
from app.core.exceptions import AuthenticationException, NotFoundError, ValidationError
from app.services.collaboration_service import CollaborationService
from app.schemas.collaboration import (
    CursorPosition,
    DocumentAnnotationCreate,
    JoinDocumentMessage,
    LeaveDocumentMessage,
    CursorUpdateMessage,
    AnnotationMessage,
    UserPresenceMessage,
    SyncRequestMessage
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


class ConnectionManager:
    """Enhanced WebSocket connection manager for real-time collaboration."""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Store task subscriptions by task_id -> user_ids
        self.task_subscriptions: Dict[str, List[str]] = {}
        # Store document session connections: session_id -> {user_id: websocket}
        self.document_sessions: Dict[str, Dict[str, WebSocket]] = {}
        # Store user presence data: session_id -> {user_id: presence_data}
        self.user_presence: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # Store connection metadata: websocket -> {user_id, session_id, etc.}
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected via WebSocket")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # Clean up empty connection lists
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Clean up task subscriptions
        for task_id, subscribers in list(self.task_subscriptions.items()):
            if user_id in subscribers:
                subscribers.remove(user_id)
                if not subscribers:
                    del self.task_subscriptions[task_id]
        
        logger.info(f"User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, message: Dict[str, Any], user_id: str):
        """Send a message to a specific user."""
        if user_id in self.active_connections:
            disconnected_connections = []
            
            for connection in self.active_connections[user_id]:
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_text(json.dumps(message))
                    else:
                        disconnected_connections.append(connection)
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {e}")
                    disconnected_connections.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected_connections:
                if conn in self.active_connections[user_id]:
                    self.active_connections[user_id].remove(conn)
    
    async def broadcast_to_subscribers(self, message: Dict[str, Any], task_id: str):
        """Broadcast a message to all subscribers of a task."""
        if task_id in self.task_subscriptions:
            for user_id in self.task_subscriptions[task_id]:
                await self.send_personal_message(message, user_id)
    
    def subscribe_to_task(self, task_id: str, user_id: str):
        """Subscribe a user to task updates."""
        if task_id not in self.task_subscriptions:
            self.task_subscriptions[task_id] = []
        
        if user_id not in self.task_subscriptions[task_id]:
            self.task_subscriptions[task_id].append(user_id)
            logger.info(f"User {user_id} subscribed to task {task_id}")
    
    def unsubscribe_from_task(self, task_id: str, user_id: str):
        """Unsubscribe a user from task updates."""
        if task_id in self.task_subscriptions and user_id in self.task_subscriptions[task_id]:
            self.task_subscriptions[task_id].remove(user_id)
            
            if not self.task_subscriptions[task_id]:
                del self.task_subscriptions[task_id]
            
            logger.info(f"User {user_id} unsubscribed from task {task_id}")
    
    async def join_document_session(
        self, 
        websocket: WebSocket, 
        session_id: str, 
        user_id: str,
        user_name: str = None
    ):
        """Join a document collaboration session."""
        if session_id not in self.document_sessions:
            self.document_sessions[session_id] = {}
            self.user_presence[session_id] = {}
        
        self.document_sessions[session_id][user_id] = websocket
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "session_id": session_id,
            "user_name": user_name,
            "joined_at": datetime.utcnow()
        }
        
        # Update user presence
        self.user_presence[session_id][user_id] = {
            "user_name": user_name or f"User {user_id}",
            "is_online": True,
            "last_seen": datetime.utcnow(),
            "cursor_position": None
        }
        
        # Notify other users in the session
        await self.broadcast_to_document_session(
            {
                "type": "user_joined",
                "user_id": user_id,
                "user_name": user_name or f"User {user_id}",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "online_users": list(self.user_presence[session_id].keys())
            },
            session_id,
            exclude_user=user_id
        )
        
        # Send current session state to the joining user
        await websocket.send_text(json.dumps({
            "type": "session_state",
            "session_id": session_id,
            "online_users": {
                uid: data for uid, data in self.user_presence[session_id].items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        logger.info(f"User {user_id} joined document session {session_id}")
    
    async def leave_document_session(self, session_id: str, user_id: str):
        """Leave a document collaboration session."""
        if session_id in self.document_sessions and user_id in self.document_sessions[session_id]:
            websocket = self.document_sessions[session_id][user_id]
            
            # Clean up connection metadata
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]
            
            del self.document_sessions[session_id][user_id]
            
            # Update user presence
            if session_id in self.user_presence and user_id in self.user_presence[session_id]:
                user_name = self.user_presence[session_id][user_id].get("user_name", f"User {user_id}")
                del self.user_presence[session_id][user_id]
                
                # Notify other users
                await self.broadcast_to_document_session(
                    {
                        "type": "user_left",
                        "user_id": user_id,
                        "user_name": user_name,
                        "session_id": session_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "online_users": list(self.user_presence[session_id].keys())
                    },
                    session_id
                )
            
            # Clean up empty sessions
            if not self.document_sessions[session_id]:
                del self.document_sessions[session_id]
                if session_id in self.user_presence:
                    del self.user_presence[session_id]
            
            logger.info(f"User {user_id} left document session {session_id}")
    
    async def update_cursor_position(
        self, 
        session_id: str, 
        user_id: str, 
        cursor_position: Dict[str, Any]
    ):
        """Update user cursor position and broadcast to other users."""
        if session_id in self.user_presence and user_id in self.user_presence[session_id]:
            self.user_presence[session_id][user_id]["cursor_position"] = cursor_position
            self.user_presence[session_id][user_id]["last_seen"] = datetime.utcnow()
            
            # Broadcast cursor update to other users
            await self.broadcast_to_document_session(
                {
                    "type": "cursor_update",
                    "user_id": user_id,
                    "user_name": self.user_presence[session_id][user_id].get("user_name"),
                    "session_id": session_id,
                    "position": cursor_position,
                    "timestamp": datetime.utcnow().isoformat()
                },
                session_id,
                exclude_user=user_id
            )
    
    async def broadcast_to_document_session(
        self, 
        message: Dict[str, Any], 
        session_id: str, 
        exclude_user: Optional[str] = None
    ):
        """Broadcast a message to all users in a document session."""
        if session_id in self.document_sessions:
            disconnected_users = []
            
            for user_id, connection in self.document_sessions[session_id].items():
                if exclude_user and user_id == exclude_user:
                    continue
                
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_text(json.dumps(message))
                    else:
                        disconnected_users.append(user_id)
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id} in session {session_id}: {e}")
                    disconnected_users.append(user_id)
            
            # Clean up disconnected users
            for user_id in disconnected_users:
                await self.leave_document_session(session_id, user_id)
    
    async def handle_annotation_conflict(
        self,
        session_id: str,
        annotation_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Handle potential annotation conflicts."""
        # Simple conflict detection based on overlapping text ranges
        if "start_offset" in annotation_data and "end_offset" in annotation_data:
            # In a real implementation, you would check against existing annotations
            # For now, we'll just return a conflict notification
            conflict_message = {
                "type": "annotation_conflict",
                "session_id": session_id,
                "user_id": user_id,
                "conflict_type": "potential_overlap",
                "annotation_data": annotation_data,
                "timestamp": datetime.utcnow().isoformat(),
                "resolution_options": ["merge", "override", "manual"]
            }
            
            return conflict_message
        
        return None
    
    def cleanup_disconnected_connections(self):
        """Clean up disconnected WebSocket connections."""
        disconnected_connections = []
        
        for websocket, metadata in self.connection_metadata.items():
            if websocket.client_state != WebSocketState.CONNECTED:
                disconnected_connections.append(websocket)
        
        for websocket in disconnected_connections:
            metadata = self.connection_metadata.get(websocket, {})
            user_id = metadata.get("user_id")
            session_id = metadata.get("session_id")
            
            if user_id and session_id:
                asyncio.create_task(self.leave_document_session(session_id, user_id))
            
            # Clean up from active connections
            if user_id and user_id in self.active_connections:
                if websocket in self.active_connections[user_id]:
                    self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]


# Global connection manager instance
connection_manager = ConnectionManager()


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """Main WebSocket endpoint for real-time communication with collaboration features."""
    user_id = None
    
    try:
        # Get user from WebSocket (you'll need to implement authentication)
        # For now, we'll extract user_id from query parameters
        user_id = websocket.query_params.get("user_id")
        if not user_id:
            await websocket.close(code=4001, reason="Missing user_id")
            return
        
        await connection_manager.connect(websocket, user_id)
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "features": [
                "real_time_collaboration",
                "document_annotations", 
                "cursor_tracking",
                "conflict_resolution",
                "sync_recovery"
            ]
        }))
        
        # Start periodic cleanup task
        cleanup_task = asyncio.create_task(periodic_cleanup())
        
        try:
            while True:
                # Receive messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await handle_websocket_message(websocket, user_id, message, db)
                
        finally:
            cleanup_task.cancel()
            
    except WebSocketDisconnect:
        if user_id:
            connection_manager.disconnect(websocket, user_id)
            # Clean up any active sessions
            metadata = connection_manager.connection_metadata.get(websocket, {})
            session_id = metadata.get("session_id")
            if session_id:
                await connection_manager.leave_document_session(session_id, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        if user_id:
            connection_manager.disconnect(websocket, user_id)


async def periodic_cleanup():
    """Periodic cleanup of disconnected connections."""
    while True:
        try:
            await asyncio.sleep(30)  # Run every 30 seconds
            connection_manager.cleanup_disconnected_connections()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")


async def handle_websocket_message(
    websocket: WebSocket, 
    user_id: str, 
    message: Dict[str, Any],
    db: Session = None
):
    """Handle incoming WebSocket messages with enhanced collaboration features."""
    message_type = message.get("type")
    
    try:
        if message_type == "subscribe_task":
            # Subscribe to task progress updates
            task_id = message.get("task_id")
            if task_id:
                connection_manager.subscribe_to_task(task_id, user_id)
                
                # Send current task status
                task_status = task_monitor.get_task_status(task_id)
                await websocket.send_text(json.dumps({
                    "type": "task_status",
                    "task_id": task_id,
                    "status": task_status
                }))
        
        elif message_type == "unsubscribe_task":
            # Unsubscribe from task updates
            task_id = message.get("task_id")
            if task_id:
                connection_manager.unsubscribe_from_task(task_id, user_id)
        
        elif message_type == "join_document":
            # Join document collaboration session
            session_id = message.get("session_id")
            user_name = message.get("user_name", f"User {user_id}")
            
            if session_id:
                # Update database if collaboration service is available
                if db:
                    try:
                        collaboration_service = CollaborationService(db)
                        await collaboration_service.join_session(
                            uuid.UUID(session_id), 
                            uuid.UUID(user_id)
                        )
                    except Exception as e:
                        logger.error(f"Failed to update database for session join: {e}")
                
                await connection_manager.join_document_session(
                    websocket, session_id, user_id, user_name
                )
        
        elif message_type == "leave_document":
            # Leave document collaboration session
            session_id = message.get("session_id")
            
            if session_id:
                # Update database if collaboration service is available
                if db:
                    try:
                        collaboration_service = CollaborationService(db)
                        await collaboration_service.leave_session(
                            uuid.UUID(session_id), 
                            uuid.UUID(user_id)
                        )
                    except Exception as e:
                        logger.error(f"Failed to update database for session leave: {e}")
                
                await connection_manager.leave_document_session(session_id, user_id)
        
        elif message_type == "document_annotation":
            # Handle document annotation updates
            session_id = message.get("session_id")
            annotation_data = message.get("annotation")
            action = message.get("action", "create")
            
            if session_id and annotation_data:
                # Check for conflicts
                conflict = await connection_manager.handle_annotation_conflict(
                    session_id, annotation_data, user_id
                )
                
                if conflict:
                    # Send conflict notification to user
                    await websocket.send_text(json.dumps(conflict))
                
                # Create annotation in database if service is available
                annotation_id = None
                if db and action == "create":
                    try:
                        collaboration_service = CollaborationService(db)
                        annotation_create = DocumentAnnotationCreate(**annotation_data)
                        created_annotation = await collaboration_service.create_annotation(
                            uuid.UUID(session_id),
                            uuid.UUID(user_id),
                            annotation_create
                        )
                        annotation_id = str(created_annotation.id)
                    except Exception as e:
                        logger.error(f"Failed to create annotation in database: {e}")
                
                # Broadcast to other users
                await connection_manager.broadcast_to_document_session(
                    {
                        "type": "annotation_update",
                        "session_id": session_id,
                        "user_id": user_id,
                        "annotation": annotation_data,
                        "annotation_id": annotation_id,
                        "action": action,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    session_id,
                    exclude_user=user_id
                )
        
        elif message_type == "cursor_position":
            # Handle cursor position updates
            session_id = message.get("session_id")
            position = message.get("position")
            
            if session_id and position:
                # Update cursor position in connection manager
                await connection_manager.update_cursor_position(session_id, user_id, position)
                
                # Update database if service is available
                if db:
                    try:
                        collaboration_service = CollaborationService(db)
                        cursor_pos = CursorPosition(**position)
                        await collaboration_service.update_user_presence(
                            uuid.UUID(session_id),
                            uuid.UUID(user_id),
                            cursor_pos
                        )
                    except Exception as e:
                        logger.error(f"Failed to update cursor position in database: {e}")
        
        elif message_type == "sync_request":
            # Handle sync request for reconnection
            session_id = message.get("session_id")
            last_sync_timestamp = message.get("last_sync_timestamp")
            
            if session_id and db:
                try:
                    collaboration_service = CollaborationService(db)
                    
                    # Get events since last sync
                    if last_sync_timestamp:
                        since_time = datetime.fromisoformat(last_sync_timestamp.replace('Z', '+00:00'))
                        events = await collaboration_service.get_session_events_since(
                            uuid.UUID(session_id),
                            since_time
                        )
                        
                        # Send sync data
                        await websocket.send_text(json.dumps({
                            "type": "sync_response",
                            "session_id": session_id,
                            "events": [
                                {
                                    "event_type": event.event_type,
                                    "user_id": str(event.user_id),
                                    "event_data": event.event_data,
                                    "timestamp": event.timestamp.isoformat()
                                }
                                for event in events
                            ],
                            "timestamp": datetime.utcnow().isoformat()
                        }))
                    
                    # Get current session state
                    annotations = await collaboration_service.get_session_annotations(
                        uuid.UUID(session_id)
                    )
                    
                    await websocket.send_text(json.dumps({
                        "type": "session_sync",
                        "session_id": session_id,
                        "annotations": [
                            {
                                "id": str(ann.id),
                                "user_id": str(ann.user_id),
                                "annotation_type": ann.annotation_type,
                                "content": ann.content,
                                "page_number": ann.page_number,
                                "start_offset": ann.start_offset,
                                "end_offset": ann.end_offset,
                                "selected_text": ann.selected_text,
                                "style_data": ann.style_data,
                                "created_at": ann.created_at.isoformat()
                            }
                            for ann in annotations
                        ],
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                    
                except Exception as e:
                    logger.error(f"Failed to handle sync request: {e}")
                    await websocket.send_text(json.dumps({
                        "type": "sync_error",
                        "message": "Failed to sync session data"
                    }))
        
        elif message_type == "ping":
            # Handle ping/pong for connection health
            await websocket.send_text(json.dumps({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            }))
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }))
    
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Failed to process message"
        }))


# Task progress notification functions
async def notify_task_progress(task_id: str, progress: int, total: int, message: str):
    """Send task progress notification to subscribers."""
    notification = {
        "type": "task_progress",
        "task_id": task_id,
        "progress": progress,
        "total": total,
        "percentage": int((progress / total) * 100) if total > 0 else 0,
        "message": message,
        "timestamp": asyncio.get_event_loop().time()
    }
    
    await connection_manager.broadcast_to_subscribers(notification, task_id)


async def notify_task_completed(task_id: str, result: Dict[str, Any]):
    """Send task completion notification to subscribers."""
    notification = {
        "type": "task_completed",
        "task_id": task_id,
        "result": result,
        "timestamp": asyncio.get_event_loop().time()
    }
    
    await connection_manager.broadcast_to_subscribers(notification, task_id)


async def notify_task_failed(task_id: str, error: str):
    """Send task failure notification to subscribers."""
    notification = {
        "type": "task_failed",
        "task_id": task_id,
        "error": error,
        "timestamp": asyncio.get_event_loop().time()
    }
    
    await connection_manager.broadcast_to_subscribers(notification, task_id)


# REST endpoints for WebSocket management
@router.get("/connections")
async def get_active_connections(current_user = Depends(get_current_user)):
    """Get information about active WebSocket connections."""
    return {
        "active_users": len(connection_manager.active_connections),
        "total_connections": sum(len(conns) for conns in connection_manager.active_connections.values()),
        "task_subscriptions": len(connection_manager.task_subscriptions),
        "document_sessions": len(connection_manager.document_sessions)
    }


@router.post("/broadcast")
async def broadcast_message(
    message: Dict[str, Any],
    target_users: Optional[List[str]] = None,
    current_user = Depends(get_current_user)
):
    """Broadcast a message to specific users or all connected users."""
    if target_users:
        for user_id in target_users:
            await connection_manager.send_personal_message(message, user_id)
    else:
        # Broadcast to all connected users
        for user_id in connection_manager.active_connections:
            await connection_manager.send_personal_message(message, user_id)
    
    return {
        "success": True,
        "message": "Message broadcasted successfully",
        "target_users": target_users or "all"
    }


# REST API endpoints for collaboration management

@router.post("/sessions", response_model=Dict[str, Any])
async def create_collaboration_session(
    session_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new document collaboration session."""
    try:
        collaboration_service = CollaborationService(db)
        
        # Validate input
        document_id = session_data.get("document_id")
        session_name = session_data.get("name", f"Session for Document {document_id}")
        
        if not document_id:
            raise ValidationError("document_id is required")
        
        from app.schemas.collaboration import DocumentSessionCreate
        session_create = DocumentSessionCreate(
            document_id=uuid.UUID(document_id),
            name=session_name
        )
        
        session = await collaboration_service.create_session(
            session_create,
            current_user.id
        )
        
        return {
            "success": True,
            "session": {
                "id": str(session.id),
                "document_id": str(session.document_id),
                "name": session.name,
                "created_by": str(session.created_by),
                "created_at": session.created_at.isoformat(),
                "is_active": session.is_active
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create collaboration session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_collaboration_session(
    session_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get collaboration session details."""
    try:
        collaboration_service = CollaborationService(db)
        
        session = await collaboration_service.get_session(uuid.UUID(session_id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        participants = await collaboration_service.get_session_participants(
            uuid.UUID(session_id)
        )
        
        annotations = await collaboration_service.get_session_annotations(
            uuid.UUID(session_id)
        )
        
        return {
            "session": {
                "id": str(session.id),
                "document_id": str(session.document_id),
                "name": session.name,
                "created_by": str(session.created_by),
                "created_at": session.created_at.isoformat(),
                "is_active": session.is_active
            },
            "participants": [
                {
                    "user_id": str(p.user_id),
                    "joined_at": p.joined_at.isoformat(),
                    "is_online": p.is_online,
                    "last_seen": p.last_seen.isoformat() if p.last_seen else None
                }
                for p in participants
            ],
            "annotations": [
                {
                    "id": str(a.id),
                    "user_id": str(a.user_id),
                    "annotation_type": a.annotation_type,
                    "content": a.content,
                    "page_number": a.page_number,
                    "start_offset": a.start_offset,
                    "end_offset": a.end_offset,
                    "created_at": a.created_at.isoformat()
                }
                for a in annotations
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get collaboration session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}/sessions", response_model=Dict[str, Any])
async def get_document_sessions(
    document_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all collaboration sessions for a document."""
    try:
        collaboration_service = CollaborationService(db)
        
        sessions = await collaboration_service.get_document_sessions(
            uuid.UUID(document_id)
        )
        
        return {
            "sessions": [
                {
                    "id": str(session.id),
                    "name": session.name,
                    "created_by": str(session.created_by),
                    "created_at": session.created_at.isoformat(),
                    "is_active": session.is_active
                }
                for session in sessions
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get document sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/annotations", response_model=Dict[str, Any])
async def create_annotation(
    session_id: str,
    annotation_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new annotation in a collaboration session."""
    try:
        collaboration_service = CollaborationService(db)
        
        from app.schemas.collaboration import DocumentAnnotationCreate
        annotation_create = DocumentAnnotationCreate(**annotation_data)
        
        annotation = await collaboration_service.create_annotation(
            uuid.UUID(session_id),
            current_user.id,
            annotation_create
        )
        
        # Broadcast to WebSocket clients
        await connection_manager.broadcast_to_document_session(
            {
                "type": "annotation_created",
                "session_id": session_id,
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
            session_id,
            exclude_user=str(current_user.id)
        )
        
        return {
            "success": True,
            "annotation": {
                "id": str(annotation.id),
                "annotation_type": annotation.annotation_type,
                "content": annotation.content,
                "created_at": annotation.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create annotation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}/annotations/{annotation_id}")
async def delete_annotation(
    session_id: str,
    annotation_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an annotation from a collaboration session."""
    try:
        collaboration_service = CollaborationService(db)
        
        success = await collaboration_service.delete_annotation(
            uuid.UUID(annotation_id),
            current_user.id
        )
        
        if success:
            # Broadcast to WebSocket clients
            await connection_manager.broadcast_to_document_session(
                {
                    "type": "annotation_deleted",
                    "session_id": session_id,
                    "annotation_id": annotation_id,
                    "user_id": str(current_user.id),
                    "timestamp": datetime.utcnow().isoformat()
                },
                session_id,
                exclude_user=str(current_user.id)
            )
        
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Failed to delete annotation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections/stats")
async def get_connection_stats(current_user = Depends(get_current_user)):
    """Get WebSocket connection statistics."""
    return {
        "active_users": len(connection_manager.active_connections),
        "total_connections": sum(len(conns) for conns in connection_manager.active_connections.values()),
        "task_subscriptions": len(connection_manager.task_subscriptions),
        "document_sessions": len(connection_manager.document_sessions),
        "total_session_participants": sum(
            len(participants) for participants in connection_manager.document_sessions.values()
        )
    }