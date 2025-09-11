"""Document schemas for API requests and responses."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

from app.database.models.document import DocumentType, AnalysisStatus, Jurisdiction


class DocumentBase(BaseModel):
    """Base document schema."""
    name: str = Field(..., min_length=1, max_length=255)
    document_type: DocumentType = DocumentType.OTHER


class DocumentCreate(DocumentBase):
    """Document creation schema (for internal use)."""
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    content: Optional[str] = None
    page_count: Optional[int] = None


class DocumentUpdate(BaseModel):
    """Document update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    document_type: Optional[DocumentType] = None
    analysis_status: Optional[AnalysisStatus] = None
    jurisdiction: Optional[Jurisdiction] = None
    detected_jurisdiction: Optional[Dict[str, Any]] = None
    document_metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(DocumentBase):
    """Document response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    original_filename: str
    file_size: int
    mime_type: str
    page_count: Optional[int] = None
    analysis_status: AnalysisStatus
    jurisdiction: Optional[Jurisdiction] = None
    detected_jurisdiction: Optional[Dict[str, Any]] = None
    document_metadata: Optional[Dict[str, Any]] = None
    uploaded_by: str
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    """Document list response schema."""
    documents: list[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int


class DocumentUploadResponse(BaseModel):
    """Document upload response schema."""
    message: str
    document: DocumentResponse


class FileUploadInfo(BaseModel):
    """File upload information."""
    filename: str
    size: int
    content_type: str