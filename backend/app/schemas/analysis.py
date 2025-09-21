"""Analysis schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Risk(BaseModel):
    """Risk identification schema."""
    description: str = Field(..., description="Risk description")
    level: RiskLevel = Field(..., description="Risk severity level")
    category: str = Field(..., description="Risk category")
    mitigation: Optional[str] = Field(None, description="Suggested mitigation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class Obligation(BaseModel):
    """Obligation extraction schema."""
    description: str = Field(..., description="Obligation description")
    party: Optional[str] = Field(None, description="Responsible party")
    deadline: Optional[str] = Field(None, description="Deadline or timeframe")
    category: str = Field(..., description="Obligation category")
    priority: str = Field(..., description="Priority level")


class KeyTerm(BaseModel):
    """Key term schema."""
    term: str = Field(..., description="Term or phrase")
    definition: Optional[str] = Field(None, description="Definition if available")
    category: str = Field(..., description="Term category")
    frequency: int = Field(..., ge=1, description="Frequency in document")


class ComplexityScore(BaseModel):
    """Document complexity scoring schema."""
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall complexity score")
    legal_complexity: float = Field(..., ge=0.0, le=100.0, description="Legal complexity")
    language_complexity: float = Field(..., ge=0.0, le=100.0, description="Language complexity")
    structure_complexity: float = Field(..., ge=0.0, le=100.0, description="Structure complexity")
    factors: List[str] = Field(..., description="Factors contributing to complexity")


class ExecutiveSummary(BaseModel):
    """Executive summary schema."""
    content: str = Field(..., description="Summary content")
    key_points: List[str] = Field(..., description="Key points")
    document_type: str = Field(..., description="Detected document type")
    parties: List[str] = Field(..., description="Identified parties")
    word_count: int = Field(..., ge=0, description="Summary word count")


class AnalysisResultsResponse(BaseModel):
    """Analysis results response schema."""
    id: str = Field(..., description="Analysis ID")
    document_id: str = Field(..., description="Document ID")
    status: AnalysisStatus = Field(..., description="Analysis status")
    
    # Analysis results
    summary: Optional[ExecutiveSummary] = Field(None, description="Executive summary")
    risks: List[Risk] = Field(default_factory=list, description="Identified risks")
    obligations: List[Obligation] = Field(default_factory=list, description="Extracted obligations")
    key_terms: List[KeyTerm] = Field(default_factory=list, description="Key terms")
    complexity_score: Optional[ComplexityScore] = Field(None, description="Complexity metrics")
    
    # Metadata
    ai_model_used: Optional[str] = Field(None, description="AI model used for analysis")
    processing_time_seconds: Optional[float] = Field(None, description="Processing time")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall confidence")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    """Analysis request schema."""
    document_id: str = Field(..., description="Document ID to analyze")
    analysis_type: Optional[str] = Field("comprehensive", description="Type of analysis to perform")
    options: Dict[str, Any] = Field(default_factory=dict, description="Analysis options")


class AnalysisProgressResponse(BaseModel):
    """Analysis progress response schema."""
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Task status")
    progress: Dict[str, Any] = Field(..., description="Progress information")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")