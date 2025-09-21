"""Authentication utilities and JWT token management with enhanced security."""

from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import secrets

from app.config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: The plain text password
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with enhanced security.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    
    # Add additional security claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(16),  # JWT ID for token revocation
        "iss": "legalease-ai",  # Issuer
        "aud": "legalease-api"  # Audience
    })
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token"
        )


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token with enhanced security checks.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        dict: The decoded token payload, or None if invalid
    """
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm],
            audience="legalease-api",
            issuer="legalease-ai"
        )
        
        # Verify required claims
        if not payload.get("sub") or not payload.get("jti"):
            logger.warning("Token missing required claims")
            return None
            
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {e}")
        return None


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: The data to encode in the token
        
    Returns:
        str: The encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # Refresh tokens last 7 days
    to_encode.update({"exp": expire, "type": "refresh"})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating refresh token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create refresh token"
        )

async def get_user_by_email(db: AsyncSession, email: str):
    """Get user by email."""
    from app.database.models.user import User
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def authenticate_user(
    db: AsyncSession, 
    email: str, 
    password: str,
    request: Optional[Request] = None
):
    """Authenticate user with email and password with audit logging."""
    from app.core.audit import audit_logger, AuditEventType
    
    client_ip = None
    user_agent = None
    
    if request:
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("user-agent")
    
    try:
        user = await get_user_by_email(db, email)
        if not user:
            # Log failed login attempt
            await audit_logger.log_authentication_event(
                AuditEventType.LOGIN_FAILED,
                ip_address=client_ip,
                user_agent=user_agent,
                details={"email": email, "reason": "user_not_found"},
                success=False
            )
            return None
        
        if not user.is_active:
            # Log failed login attempt for inactive user
            await audit_logger.log_authentication_event(
                AuditEventType.LOGIN_FAILED,
                user_id=str(user.id),
                ip_address=client_ip,
                user_agent=user_agent,
                details={"email": email, "reason": "user_inactive"},
                success=False
            )
            return None
        
        if not verify_password(password, user.hashed_password):
            # Log failed login attempt
            await audit_logger.log_authentication_event(
                AuditEventType.LOGIN_FAILED,
                user_id=str(user.id),
                ip_address=client_ip,
                user_agent=user_agent,
                details={"email": email, "reason": "invalid_password"},
                success=False
            )
            return None
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        await db.commit()
        
        # Log successful login
        await audit_logger.log_authentication_event(
            AuditEventType.USER_LOGIN,
            user_id=str(user.id),
            ip_address=client_ip,
            user_agent=user_agent,
            details={"email": email},
            success=True
        )
        
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        # Log system error
        await audit_logger.log_authentication_event(
            AuditEventType.LOGIN_FAILED,
            ip_address=client_ip,
            user_agent=user_agent,
            details={"email": email, "reason": "system_error", "error": str(e)},
            success=False
        )
        return None


async def create_user(
    db: AsyncSession, 
    email: str, 
    password: str, 
    name: str, 
    organization: Optional[str] = None,
    request: Optional[Request] = None
):
    """Create a new user with enhanced security and audit logging."""
    from app.database.models.user import User
    from app.core.audit import audit_logger, AuditEventType
    
    client_ip = None
    user_agent = None
    
    if request:
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("user-agent")
    
    try:
        # Check if user already exists
        existing_user = await get_user_by_email(db, email)
        if existing_user:
            # Log registration attempt with existing email
            await audit_logger.log_authentication_event(
                AuditEventType.USER_REGISTRATION,
                ip_address=client_ip,
                user_agent=user_agent,
                details={"email": email, "reason": "email_already_exists"},
                success=False
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user with enhanced password hashing
        hashed_password = get_password_hash(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            name=name,
            organization=organization,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Log successful registration
        await audit_logger.log_authentication_event(
            AuditEventType.USER_REGISTRATION,
            user_id=str(user.id),
            ip_address=client_ip,
            user_agent=user_agent,
            details={"email": email, "name": name, "organization": organization},
            success=True
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User creation error: {e}")
        # Log system error
        await audit_logger.log_authentication_event(
            AuditEventType.USER_REGISTRATION,
            ip_address=client_ip,
            user_agent=user_agent,
            details={"email": email, "reason": "system_error", "error": str(e)},
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed"
        )


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    # Check for forwarded headers (when behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return request.client.host if request.client else "unknown"


class SecureTokenManager:
    """Enhanced token management with encryption and audit logging."""
    
    @staticmethod
    async def create_api_token(user_id: str, name: str, expires_hours: int = 24 * 30) -> str:
        """Create encrypted API token."""
        from app.core.encryption import token_manager
        from app.core.audit import audit_logger, AuditEventType
        
        token_data = {
            "user_id": user_id,
            "token_name": name,
            "type": "api_token"
        }
        
        token = token_manager.create_token(token_data, expires_hours)
        
        # Log token creation
        await audit_logger.log_authentication_event(
            AuditEventType.USER_LOGIN,  # Using login event for API token creation
            user_id=user_id,
            details={"token_name": name, "expires_hours": expires_hours, "type": "api_token"},
            success=True
        )
        
        return token
    
    @staticmethod
    async def verify_api_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify encrypted API token."""
        from app.core.encryption import token_manager
        
        try:
            token_data = token_manager.verify_token(token)
            if token_data and token_data.get("type") == "api_token":
                return token_data
            return None
        except Exception as e:
            logger.warning(f"API token verification failed: {e}")
            return None