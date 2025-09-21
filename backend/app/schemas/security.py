"""Security-related Pydantic schemas with comprehensive validation."""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

from app.core.security import (
    InputValidator, 
    SecureStringField, 
    SecureEmailField, 
    SecureFilenameField,
    SecureBaseModel
)


class SecureDocumentUpload(SecureBaseModel):
    """Secure document upload schema with validation."""
    
    name: Optional[SecureStringField] = Field(
        None,
        description="Document name",
        max_length=255
    )
    
    document_type: str = Field(
        ...,
        description="Document type",
        regex=r"^[A-Z_]+$"
    )
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            return InputValidator.validate_string(v, max_length=255)
        return v


class SecureUserRegistration(SecureBaseModel):
    """Secure user registration schema."""
    
    email: SecureEmailField = Field(
        ...,
        description="User email address"
    )
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password"
    )
    
    name: SecureStringField = Field(
        ...,
        min_length=2,
        max_length=100,
        description="User full name"
    )
    
    organization: Optional[SecureStringField] = Field(
        None,
        max_length=200,
        description="User organization"
    )
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '12345678', 'qwerty123', 'admin123',
            'password123', 'letmein123', 'welcome123'
        ]
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common')
        
        return v


class SecureUserLogin(SecureBaseModel):
    """Secure user login schema."""
    
    email: SecureEmailField = Field(
        ...,
        description="User email address"
    )
    
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="User password"
    )


class SecureDocumentUpdate(SecureBaseModel):
    """Secure document update schema."""
    
    name: Optional[SecureStringField] = Field(
        None,
        max_length=255,
        description="Document name"
    )
    
    document_type: Optional[str] = Field(
        None,
        regex=r"^[A-Z_]+$",
        description="Document type"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Document metadata"
    )
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate metadata structure."""
        if v is None:
            return v
        
        if not isinstance(v, dict):
            raise ValueError('Metadata must be a dictionary')
        
        # Limit metadata size
        if len(str(v)) > 10000:
            raise ValueError('Metadata too large')
        
        # Validate metadata keys and values
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError('Metadata keys must be strings')
            
            if len(key) > 100:
                raise ValueError('Metadata key too long')
            
            # Validate key format
            if not re.match(r'^[a-zA-Z0-9_-]+$', key):
                raise ValueError(f'Invalid metadata key format: {key}')
            
            # Validate value
            if isinstance(value, str):
                InputValidator.validate_string(value, max_length=1000)
            elif not isinstance(value, (int, float, bool, type(None))):
                raise ValueError(f'Invalid metadata value type for key {key}')
        
        return v


class SecureChatMessage(SecureBaseModel):
    """Secure chat message schema."""
    
    message: SecureStringField = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Chat message content"
    )
    
    document_id: Optional[str] = Field(
        None,
        regex=r'^[a-zA-Z0-9\-_]{1,50}$',
        description="Associated document ID"
    )
    
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Message context"
    )
    
    @validator('context')
    def validate_context(cls, v):
        """Validate message context."""
        if v is None:
            return v
        
        if not isinstance(v, dict):
            raise ValueError('Context must be a dictionary')
        
        # Limit context size
        if len(str(v)) > 5000:
            raise ValueError('Context too large')
        
        return v


class SecureSearchQuery(SecureBaseModel):
    """Secure search query schema."""
    
    query: SecureStringField = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Search query"
    )
    
    filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Search filters"
    )
    
    limit: Optional[int] = Field(
        10,
        ge=1,
        le=100,
        description="Result limit"
    )
    
    offset: Optional[int] = Field(
        0,
        ge=0,
        description="Result offset"
    )
    
    @validator('filters')
    def validate_filters(cls, v):
        """Validate search filters."""
        if v is None:
            return v
        
        if not isinstance(v, dict):
            raise ValueError('Filters must be a dictionary')
        
        allowed_filter_keys = {
            'document_type', 'jurisdiction', 'date_from', 'date_to',
            'user_id', 'organization', 'tags'
        }
        
        for key in v.keys():
            if key not in allowed_filter_keys:
                raise ValueError(f'Invalid filter key: {key}')
        
        return v


class SecureAnnotation(SecureBaseModel):
    """Secure annotation schema."""
    
    content: SecureStringField = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Annotation content"
    )
    
    page_number: int = Field(
        ...,
        ge=1,
        le=10000,
        description="Page number"
    )
    
    position: Dict[str, float] = Field(
        ...,
        description="Annotation position"
    )
    
    annotation_type: str = Field(
        ...,
        regex=r'^[A-Z_]+$',
        description="Annotation type"
    )
    
    @validator('position')
    def validate_position(cls, v):
        """Validate annotation position."""
        if not isinstance(v, dict):
            raise ValueError('Position must be a dictionary')
        
        required_keys = {'x', 'y', 'width', 'height'}
        if not all(key in v for key in required_keys):
            raise ValueError(f'Position must contain keys: {required_keys}')
        
        for key, value in v.items():
            if not isinstance(value, (int, float)):
                raise ValueError(f'Position {key} must be a number')
            
            if value < 0 or value > 10000:
                raise ValueError(f'Position {key} out of valid range')
        
        return v


class FileUploadValidation(SecureBaseModel):
    """File upload validation result."""
    
    valid: bool = Field(..., description="Whether file is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    file_info: Dict[str, Any] = Field(default_factory=dict, description="File information")


class SecurityAuditLog(SecureBaseModel):
    """Security audit log entry."""
    
    event_type: str = Field(
        ...,
        regex=r'^[A-Z_]+$',
        description="Event type"
    )
    
    user_id: Optional[str] = Field(
        None,
        regex=r'^[a-zA-Z0-9\-_]{1,50}$',
        description="User ID"
    )
    
    resource_id: Optional[str] = Field(
        None,
        regex=r'^[a-zA-Z0-9\-_]{1,50}$',
        description="Resource ID"
    )
    
    ip_address: str = Field(
        ...,
        description="Client IP address"
    )
    
    user_agent: Optional[str] = Field(
        None,
        max_length=500,
        description="User agent"
    )
    
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Event details"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Event timestamp"
    )
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        """Validate IP address format."""
        # Basic IP validation (IPv4 and IPv6)
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        
        if not (re.match(ipv4_pattern, v) or re.match(ipv6_pattern, v)):
            # Allow 'unknown' for cases where IP cannot be determined
            if v != 'unknown':
                raise ValueError('Invalid IP address format')
        
        return v