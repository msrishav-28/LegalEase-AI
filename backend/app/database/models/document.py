"""Document model for file storage and metadata."""

from sqlalchemy import Column, String, Text, Integer, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from .base import BaseModel


class DocumentType(str, enum.Enum):
    """Document type enumeration."""
    CONTRACT = "contract"
    AGREEMENT = "agreement"
    LEGAL_NOTICE = "legal_notice"
    COMPLIANCE = "compliance"
    OTHER = "other"


class AnalysisStatus(str, enum.Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Jurisdiction(str, enum.Enum):
    """Jurisdiction enumeration."""
    INDIA = "IN"
    USA = "US"
    CROSS_BORDER = "CROSS_BORDER"


class Document(BaseModel):
    """Document model for storing uploaded files and metadata."""
    
    __tablename__ = "documents"
    
    # Basic document information
    name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Document content and metadata
    content = Column(Text, nullable=True)  # Extracted text content
    page_count = Column(Integer, nullable=True)
    document_type = Column(SQLEnum(DocumentType), default=DocumentType.OTHER)
    
    # Analysis status and results
    analysis_status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    
    # Jurisdiction information
    jurisdiction = Column(SQLEnum(Jurisdiction), nullable=True)
    detected_jurisdiction = Column(JSON, nullable=True)  # JurisdictionDetection data
    
    # Document metadata (parties, dates, etc.)
    document_metadata = Column(JSON, nullable=True)
    
    # Relationships
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    uploaded_by_user = relationship("User", back_populates="documents")
    analysis_results = relationship("AnalysisResults", back_populates="document", cascade="all, delete-orphan")
    jurisdiction_analysis = relationship("JurisdictionAnalysis", back_populates="document", cascade="all, delete-orphan")
    sessions = relationship("DocumentSession", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Document(id={self.id}, name={self.name}, status={self.analysis_status})>"