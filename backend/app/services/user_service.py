"""User service for user management operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Optional
import logging
import uuid

from app.database.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserUpdate
from app.core.auth import get_password_hash, verify_password

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user management operations."""
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            user_data: User creation data
            
        Returns:
            User: The created user
            
        Raises:
            HTTPException: If user already exists
        """
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        
        # Create new user
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            name=user_data.name,
            organization=user_data.organization,
            role=user_data.role,
            is_active=True,
            is_verified=False
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Created new user: {user.email}")
        return user
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: User password
            
        Returns:
            User: The authenticated user, or None if authentication fails
        """
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User: The user, or None if not found
        """
        try:
            # Convert string to UUID if needed
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
            
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except ValueError:
            return None
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User: The user, or None if not found
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user(db: AsyncSession, user: User, user_data: UserUpdate) -> User:
        """
        Update a user.
        
        Args:
            db: Database session
            user: The user to update
            user_data: Update data
            
        Returns:
            User: The updated user
        """
        update_data = user_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Updated user: {user.email}")
        return user
    
    @staticmethod
    async def change_password(db: AsyncSession, user: User, current_password: str, new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            db: Database session
            user: The user
            current_password: Current password
            new_password: New password
            
        Returns:
            bool: True if password was changed successfully
            
        Raises:
            HTTPException: If current password is incorrect
        """
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        user.hashed_password = get_password_hash(new_password)
        await db.commit()
        
        logger.info(f"Password changed for user: {user.email}")
        return True
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user: User) -> User:
        """
        Deactivate a user.
        
        Args:
            db: Database session
            user: The user to deactivate
            
        Returns:
            User: The deactivated user
        """
        user.is_active = False
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Deactivated user: {user.email}")
        return user