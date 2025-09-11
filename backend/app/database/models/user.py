"""User model for authentication and user management."""

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class UserRole(str, enum.Enum):
    """User roles enumeration."""
    ADMIN = "admin"
    LAWYER = "lawyer"
    ANALYST = "analyst"
    USER = "user"


class User(BaseModel):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    documents = relationship("Document", back_populates="uploaded_by_user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"