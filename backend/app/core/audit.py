"""Audit logging system for security and compliance."""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import asyncio
from contextlib import asynccontextmanager

from app.database.models.user import User
from app.core.encryption import data_encryption


class AuditEventType(Enum):
    """Audit event types."""
    
    # Authentication events
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    USER_REGISTRATION = "USER_REGISTRATION"
    LOGIN_FAILED = "LOGIN_FAILED"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    
    # Document events
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    DOCUMENT_VIEWED = "DOCUMENT_VIEWED"
    DOCUMENT_DOWNLOADED = "DOCUMENT_DOWNLOADED"
    DOCUMENT_UPDATED = "DOCUMENT_UPDATED"
    DOCUMENT_DELETED = "DOCUMENT_DELETED"
    DOCUMENT_SHARED = "DOCUMENT_SHARED"
    
    # Analysis events
    ANALYSIS_STARTED = "ANALYSIS_STARTED"
    ANALYSIS_COMPLETED = "ANALYSIS_COMPLETED"
    ANALYSIS_FAILED = "ANALYSIS_FAILED"
    
    # Security events
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    MALICIOUS_REQUEST = "MALICIOUS_REQUEST"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    FILE_VALIDATION_FAILED = "FILE_VALIDATION_FAILED"
    
    # System events
    SYSTEM_STARTUP = "SYSTEM_STARTUP"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    
    # Data events
    DATA_EXPORT = "DATA_EXPORT"
    DATA_IMPORT = "DATA_IMPORT"
    DATA_ANONYMIZED = "DATA_ANONYMIZED"
    BACKUP_CREATED = "BACKUP_CREATED"


class AuditSeverity(Enum):
    """Audit event severity levels."""
    
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class AuditEvent:
    """Audit event data structure."""
    
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: Optional[str] = None
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['severity'] = self.severity.value
        data['timestamp'] = self.timestamp.isoformat() if self.timestamp else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEvent':
        """Create from dictionary."""
        data['event_type'] = AuditEventType(data['event_type'])
        data['severity'] = AuditSeverity(data['severity'])
        if data.get('timestamp'):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class AuditLogger:
    """Centralized audit logging system."""
    
    def __init__(self):
        self.logger = logging.getLogger('audit')
        self.events_buffer: List[AuditEvent] = []
        self.buffer_size = 100
        self.encrypt_sensitive = True
        
        # Configure audit logger
        if not self.logger.handlers:
            handler = logging.FileHandler('audit.log')
            formatter = logging.Formatter(
                '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    async def log_event(self, event: AuditEvent):
        """Log audit event."""
        try:
            # Add to buffer
            self.events_buffer.append(event)
            
            # Prepare log data
            log_data = event.to_dict()
            
            # Encrypt sensitive details if needed
            if self.encrypt_sensitive and event.details:
                sensitive_fields = self._get_sensitive_fields(event.details)
                if sensitive_fields:
                    encrypted_details = {}
                    for key, value in event.details.items():
                        if key in sensitive_fields and isinstance(value, str):
                            encrypted_details[key] = data_encryption.encrypt_data(value)
                        else:
                            encrypted_details[key] = value
                    log_data['details'] = encrypted_details
            
            # Log to file
            log_message = json.dumps(log_data, default=str)
            
            if event.severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
                self.logger.error(log_message)
            elif event.severity == AuditSeverity.MEDIUM:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
            
            # Flush buffer if full
            if len(self.events_buffer) >= self.buffer_size:
                await self._flush_buffer()
                
        except Exception as e:
            # Fallback logging - never let audit logging break the application
            self.logger.error(f"Failed to log audit event: {e}")
    
    async def log_authentication_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True
    ):
        """Log authentication-related event."""
        severity = AuditSeverity.LOW if success else AuditSeverity.MEDIUM
        
        if event_type == AuditEventType.LOGIN_FAILED:
            severity = AuditSeverity.HIGH
        
        event = AuditEvent(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        
        await self.log_event(event)
    
    async def log_document_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        document_id: str,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log document-related event."""
        severity = AuditSeverity.LOW
        
        if event_type in [AuditEventType.DOCUMENT_DELETED, AuditEventType.DOCUMENT_SHARED]:
            severity = AuditSeverity.MEDIUM
        
        event = AuditEvent(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            resource_id=document_id,
            resource_type="document",
            ip_address=ip_address,
            details=details
        )
        
        await self.log_event(event)
    
    async def log_security_event(
        self,
        event_type: AuditEventType,
        ip_address: str,
        user_agent: Optional[str] = None,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log security-related event."""
        severity = AuditSeverity.HIGH
        
        if event_type == AuditEventType.MALICIOUS_REQUEST:
            severity = AuditSeverity.CRITICAL
        
        event = AuditEvent(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        
        await self.log_event(event)
    
    async def log_system_event(
        self,
        event_type: AuditEventType,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.LOW
    ):
        """Log system-related event."""
        event = AuditEvent(
            event_type=event_type,
            severity=severity,
            details=details
        )
        
        await self.log_event(event)
    
    async def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[AuditEventType]] = None,
        user_id: Optional[str] = None,
        severity: Optional[AuditSeverity] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Retrieve audit events with filtering."""
        # This would typically query a database
        # For now, return from buffer (in production, implement database storage)
        
        filtered_events = []
        
        for event in self.events_buffer:
            # Apply filters
            if start_date and event.timestamp < start_date:
                continue
            if end_date and event.timestamp > end_date:
                continue
            if event_types and event.event_type not in event_types:
                continue
            if user_id and event.user_id != user_id:
                continue
            if severity and event.severity != severity:
                continue
            
            filtered_events.append(event)
        
        # Sort by timestamp (newest first) and limit
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
        return filtered_events[:limit]
    
    async def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get security events summary for the last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        security_events = await self.get_events(
            start_date=cutoff,
            event_types=[
                AuditEventType.RATE_LIMIT_EXCEEDED,
                AuditEventType.MALICIOUS_REQUEST,
                AuditEventType.UNAUTHORIZED_ACCESS,
                AuditEventType.LOGIN_FAILED,
                AuditEventType.FILE_VALIDATION_FAILED
            ]
        )
        
        summary = {
            'total_security_events': len(security_events),
            'events_by_type': {},
            'events_by_severity': {},
            'top_ips': {},
            'time_period_hours': hours
        }
        
        for event in security_events:
            # Count by type
            event_type = event.event_type.value
            summary['events_by_type'][event_type] = summary['events_by_type'].get(event_type, 0) + 1
            
            # Count by severity
            severity = event.severity.value
            summary['events_by_severity'][severity] = summary['events_by_severity'].get(severity, 0) + 1
            
            # Count by IP
            if event.ip_address:
                summary['top_ips'][event.ip_address] = summary['top_ips'].get(event.ip_address, 0) + 1
        
        return summary
    
    async def _flush_buffer(self):
        """Flush events buffer to persistent storage."""
        # In production, this would write to database
        # For now, just clear the buffer to prevent memory issues
        if len(self.events_buffer) > self.buffer_size * 2:
            # Keep only recent events
            self.events_buffer = self.events_buffer[-self.buffer_size:]
    
    def _get_sensitive_fields(self, details: Dict[str, Any]) -> set:
        """Identify sensitive fields that should be encrypted."""
        sensitive_keywords = {
            'password', 'token', 'key', 'secret', 'ssn', 'credit_card',
            'bank_account', 'personal_data', 'private', 'confidential'
        }
        
        sensitive_fields = set()
        for key in details.keys():
            if any(keyword in key.lower() for keyword in sensitive_keywords):
                sensitive_fields.add(key)
        
        return sensitive_fields


class AuditMiddleware:
    """Middleware for automatic audit logging."""
    
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
    
    @asynccontextmanager
    async def log_request(self, request, user_id: Optional[str] = None):
        """Context manager for logging request events."""
        start_time = datetime.utcnow()
        
        try:
            yield
            
            # Log successful request
            if request.url.path.startswith('/api/v1/documents'):
                if request.method == 'POST':
                    await self.audit_logger.log_document_event(
                        AuditEventType.DOCUMENT_UPLOADED,
                        user_id=user_id or 'anonymous',
                        document_id='pending',
                        ip_address=self._get_client_ip(request)
                    )
                elif request.method == 'GET':
                    document_id = self._extract_document_id(request.url.path)
                    if document_id:
                        await self.audit_logger.log_document_event(
                            AuditEventType.DOCUMENT_VIEWED,
                            user_id=user_id or 'anonymous',
                            document_id=document_id,
                            ip_address=self._get_client_ip(request)
                        )
            
        except Exception as e:
            # Log failed request
            await self.audit_logger.log_system_event(
                AuditEventType.DATABASE_ERROR,
                details={'error': str(e), 'path': request.url.path},
                severity=AuditSeverity.HIGH
            )
            raise
    
    def _get_client_ip(self, request) -> str:
        """Extract client IP from request."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _extract_document_id(self, path: str) -> Optional[str]:
        """Extract document ID from URL path."""
        parts = path.split('/')
        if len(parts) >= 4 and parts[3] == 'documents' and len(parts) > 4:
            return parts[4]
        return None


# Global audit logger instance
audit_logger = AuditLogger()
audit_middleware = AuditMiddleware(audit_logger)