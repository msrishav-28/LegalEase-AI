"""FastAPI dependencies for authentication and authorization."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import logging

from app.database import get_db
from app.database.models.user import User, UserRole
from app.core.auth import verify_token

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the token
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        # Extract user ID from token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: The current user from get_current_user
        
    Returns:
        User: The active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


def require_role(required_role: UserRole):
    """
    Create a dependency that requires a specific user role.
    
    Args:
        required_role: The required user role
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_role.value} role"
            )
        return current_user
    
    return role_checker


def require_roles(required_roles: list[UserRole]):
    """
    Create a dependency that requires one of several user roles.
    
    Args:
        required_roles: List of acceptable user roles
        
    Returns:
        Dependency function that checks user role
    """
    async def roles_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in required_roles:
            role_names = [role.value for role in required_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of these roles: {', '.join(role_names)}"
            )
        return current_user
    
    return roles_checker


# Common role dependencies
require_admin = require_role(UserRole.ADMIN)
require_lawyer = require_roles([UserRole.ADMIN, UserRole.LAWYER])
require_analyst = require_roles([UserRole.ADMIN, UserRole.LAWYER, UserRole.ANALYST])


async def get_current_user_websocket(token: str, db: AsyncSession) -> Optional[User]:
    """
    Get the current authenticated user from JWT token for WebSocket connections.
    
    Args:
        token: JWT token string
        db: Database session
        
    Returns:
        User: The authenticated user or None if authentication fails
    """
    try:
        # Verify the token
        payload = verify_token(token)
        if payload is None:
            return None
        
        # Extract user ID from token
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user is None or not user.is_active:
            return None
        
        return user
        
    except Exception as e:
        logger.error(f"Error getting current user for WebSocket: {e}")
        return None