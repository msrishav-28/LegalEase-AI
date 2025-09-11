"""Base model with common fields."""

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database.connection import Base


class BaseModel(Base):
    """Base model with common fields for all entities."""
    
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )