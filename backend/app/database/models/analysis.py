"""Analysis results models."""

from sqlalchemy import Column, String, Text, JSON, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from .base import BaseModel


class AnalysisStatus(str, enum.Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisResults(BaseModel):
    """Model for storing AI analysis results."""
    
    __tablename__ = "analysis_results"
    
    # Reference to document
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    document = relationship("Document", back_populates="analysis_results")
    
    # Analysis status
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    error_message = Column(Text, nullable=True)
    
    # Analysis results
    summary = Column(JSON, nullable=True)  # Executive summary
    key_terms = Column(JSON, nullable=True)  # List of key terms
    risks = Column(JSON, nullable=True)  # List of identified risks
    obligations = Column(JSON, nullable=True)  # List of obligations
    complexity_score = Column(JSON, nullable=True)  # Complexity metrics
    
    # AI metadata
    ai_model_used = Column(String(100), nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    def __repr__(self) -> str:
        return f"<AnalysisResults(id={self.id}, document_id={self.document_id}, status={self.status})>"


class JurisdictionType(str, enum.Enum):
    """Jurisdiction type enumeration."""
    INDIA = "INDIA"
    USA = "USA"
    CROSS_BORDER = "CROSS_BORDER"


class JurisdictionAnalysis(BaseModel):
    """Model for storing jurisdiction-specific analysis results."""
    
    __tablename__ = "jurisdiction_analysis"
    
    # Reference to document
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    document = relationship("Document", back_populates="jurisdiction_analysis")
    
    # Jurisdiction information
    jurisdiction = Column(SQLEnum(JurisdictionType), nullable=False)
    confidence_score = Column(Float, nullable=True)
    
    # Analysis results (jurisdiction-specific)
    analysis_results = Column(JSON, nullable=False)
    
    # Processing metadata
    processing_time_seconds = Column(Float, nullable=True)
    
    def __repr__(self) -> str:
        return f"<JurisdictionAnalysis(id={self.id}, document_id={self.document_id}, jurisdiction={self.jurisdiction})>"