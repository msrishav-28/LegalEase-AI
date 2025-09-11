"""Database package for LegalEase AI."""

from .connection import Base, get_db, init_db, close_db, engine, AsyncSessionLocal
from .models import User, Document

__all__ = [
    "Base",
    "get_db", 
    "init_db",
    "close_db",
    "engine",
    "AsyncSessionLocal",
    "User",
    "Document",
]