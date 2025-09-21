"""Security utilities and validation middleware."""

import re
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import logging
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict
import magic
import os

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration constants."""
    
    # File upload security
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'text/rtf'
    }
    
    # Input validation
    MAX_STRING_LENGTH = 10000
    MAX_TEXT_LENGTH = 1000000  # 1MB of text
    
    # Rate limiting
    DEFAULT_RATE_LIMIT = 100  # requests per minute
    BURST_RATE_LIMIT = 20  # requests per 10 seconds
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(\b(UNION|OR|AND)\s+\d+\s*=\s*\d+)",
        r"(--|#|/\*|\*/)",
        r"(\b(SCRIPT|JAVASCRIPT|VBSCRIPT|ONLOAD|ONERROR)\b)",
        r"(<script|</script>|<iframe|</iframe>)",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
    ]


class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_string(value: str, max_length: int = SecurityConfig.MAX_STRING_LENGTH) -> str:
        """Validate and sanitize string input."""
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        if len(value) > max_length:
            raise ValueError(f"String length exceeds maximum of {max_length} characters")
        
        # Check for SQL injection patterns
        for pattern in SecurityConfig.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Potentially malicious SQL pattern detected")
        
        # Check for XSS patterns
        for pattern in SecurityConfig.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Potentially malicious XSS pattern detected")
        
        return value.strip()
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        return email.lower().strip()
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """Validate and sanitize filename."""
        if not filename:
            raise ValueError("Filename cannot be empty")
        
        # Remove path traversal attempts
        filename = os.path.basename(filename)
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
        for char in dangerous_chars:
            if char in filename:
                raise ValueError(f"Filename contains invalid character: {char}")
        
        # Limit length
        if len(filename) > 255:
            raise ValueError("Filename too long")
        
        return filename
    
    @staticmethod
    def validate_document_id(doc_id: str) -> str:
        """Validate document ID format."""
        if not re.match(r'^[a-zA-Z0-9\-_]{1,50}$', doc_id):
            raise ValueError("Invalid document ID format")
        return doc_id


class FileValidator:
    """File upload validation utilities."""
    
    @staticmethod
    async def validate_file_upload(file_content: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        """Comprehensive file validation."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'file_info': {}
        }
        
        # Size validation
        if len(file_content) > SecurityConfig.MAX_FILE_SIZE:
            validation_result['valid'] = False
            validation_result['errors'].append(
                f"File size {len(file_content)} exceeds maximum of {SecurityConfig.MAX_FILE_SIZE} bytes"
            )
        
        # MIME type validation
        if mime_type not in SecurityConfig.ALLOWED_MIME_TYPES:
            validation_result['valid'] = False
            validation_result['errors'].append(f"File type {mime_type} not allowed")
        
        # Magic number validation (actual file type detection)
        try:
            detected_mime = magic.from_buffer(file_content, mime=True)
            if detected_mime != mime_type:
                validation_result['warnings'].append(
                    f"Declared MIME type {mime_type} doesn't match detected type {detected_mime}"
                )
                # Update to detected type if it's allowed
                if detected_mime in SecurityConfig.ALLOWED_MIME_TYPES:
                    mime_type = detected_mime
                else:
                    validation_result['valid'] = False
                    validation_result['errors'].append(f"Detected file type {detected_mime} not allowed")
        except Exception as e:
            logger.warning(f"Could not detect file type: {e}")
            validation_result['warnings'].append("Could not verify file type")
        
        # Filename validation
        try:
            InputValidator.validate_filename(filename)
        except ValueError as e:
            validation_result['valid'] = False
            validation_result['errors'].append(str(e))
        
        # Malware scanning (basic checks)
        if await FileValidator._basic_malware_scan(file_content):
            validation_result['valid'] = False
            validation_result['errors'].append("File failed security scan")
        
        validation_result['file_info'] = {
            'size': len(file_content),
            'mime_type': mime_type,
            'filename': filename
        }
        
        return validation_result
    
    @staticmethod
    async def _basic_malware_scan(file_content: bytes) -> bool:
        """Basic malware pattern detection."""
        # Check for common malware signatures
        malware_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'data:text/html',
            b'<?php',
            b'<%',
        ]
        
        content_lower = file_content.lower()
        for pattern in malware_patterns:
            if pattern in content_lower:
                logger.warning(f"Potential malware pattern detected: {pattern}")
                return True
        
        return False


class RateLimiter:
    """Rate limiting implementation."""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = defaultdict(datetime)
    
    async def is_allowed(self, client_ip: str, endpoint: str = "default") -> bool:
        """Check if request is allowed based on rate limits."""
        now = datetime.utcnow()
        key = f"{client_ip}:{endpoint}"
        
        # Check if IP is temporarily blocked
        if client_ip in self.blocked_ips:
            if now < self.blocked_ips[client_ip]:
                return False
            else:
                del self.blocked_ips[client_ip]
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Check rate limit
        if len(self.requests[key]) >= SecurityConfig.DEFAULT_RATE_LIMIT:
            # Block IP for 5 minutes
            self.blocked_ips[client_ip] = now + timedelta(minutes=5)
            logger.warning(f"Rate limit exceeded for IP {client_ip}, blocking for 5 minutes")
            return False
        
        # Check burst limit
        recent_requests = [
            req_time for req_time in self.requests[key]
            if now - req_time < timedelta(seconds=10)
        ]
        
        if len(recent_requests) >= SecurityConfig.BURST_RATE_LIMIT:
            logger.warning(f"Burst rate limit exceeded for IP {client_ip}")
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


class SecureBaseModel(BaseModel):
    """Base model with security validation."""
    
    class Config:
        # Prevent extra fields
        extra = "forbid"
        # Validate assignment
        validate_assignment = True
        # Use enum values
        use_enum_values = True


class SecureStringField(str):
    """Secure string field with validation."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        return InputValidator.validate_string(v)


class SecureEmailField(str):
    """Secure email field with validation."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        return InputValidator.validate_email(v)


class SecureFilenameField(str):
    """Secure filename field with validation."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        return InputValidator.validate_filename(v)


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash password with salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Use PBKDF2 with SHA-256
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # iterations
    )
    
    return password_hash.hex(), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify password against hash."""
    computed_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, password_hash)


class SecurityHeaders:
    """Security headers for HTTP responses."""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }