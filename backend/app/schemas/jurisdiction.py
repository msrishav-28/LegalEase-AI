"""Jurisdiction schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class JurisdictionType(str, Enum):
    """Jurisdiction type enumeration."""
    INDIA = "INDIA"
    USA = "USA"
    CROSS_BORDER = "CROSS_BORDER"


class JurisdictionDetectionResponse(BaseModel):
    """Jurisdiction detection response schema."""
    jurisdiction: JurisdictionType = Field(..., description="Detected jurisdiction")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    scores: Dict[str, float] = Field(..., description="Jurisdiction scores")
    us_state: Optional[str] = Field(None, description="US state if applicable")
    detected_elements: List[str] = Field(..., description="Elements that indicated jurisdiction")


class IndianLegalAnalysis(BaseModel):
    """Indian legal system analysis schema."""
    applicable_acts: List[Dict[str, Any]] = Field(..., description="Applicable Indian acts")
    stamp_duty: Dict[str, Any] = Field(..., description="Stamp duty analysis")
    gst_implications: Dict[str, Any] = Field(..., description="GST implications")
    registration_requirements: List[Dict[str, Any]] = Field(..., description="Registration requirements")
    compliance_checklist: List[Dict[str, Any]] = Field(..., description="Compliance items")


class USLegalAnalysis(BaseModel):
    """US legal system analysis schema."""
    federal_regulations: List[Dict[str, Any]] = Field(..., description="Applicable federal regulations")
    state_jurisdiction: Optional[str] = Field(None, description="State jurisdiction")
    ucc_analysis: Dict[str, Any] = Field(..., description="UCC compliance analysis")
    securities_compliance: Dict[str, Any] = Field(..., description="Securities law compliance")
    privacy_compliance: Dict[str, Any] = Field(..., description="Privacy law compliance")


class CrossBorderAnalysis(BaseModel):
    """Cross-border legal analysis schema."""
    enforceability_comparison: Dict[str, Any] = Field(..., description="Enforceability comparison")
    formalities_comparison: Dict[str, Any] = Field(..., description="Legal formalities comparison")
    tax_implications: Dict[str, Any] = Field(..., description="Tax implications")
    recommended_governing_law: str = Field(..., description="Recommended governing law")
    dispute_resolution_recommendation: str = Field(..., description="Dispute resolution recommendation")
    compliance_gaps: List[Dict[str, Any]] = Field(..., description="Compliance gaps identified")


class JurisdictionAnalysisResponse(BaseModel):
    """Jurisdiction analysis response schema."""
    id: str = Field(..., description="Analysis ID")
    document_id: str = Field(..., description="Document ID")
    jurisdiction: JurisdictionType = Field(..., description="Jurisdiction type")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Analysis confidence")
    
    # Jurisdiction-specific analysis
    indian_analysis: Optional[IndianLegalAnalysis] = Field(None, description="Indian legal analysis")
    us_analysis: Optional[USLegalAnalysis] = Field(None, description="US legal analysis")
    cross_border_analysis: Optional[CrossBorderAnalysis] = Field(None, description="Cross-border analysis")
    
    # Metadata
    processing_time_seconds: Optional[float] = Field(None, description="Processing time")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class JurisdictionAnalysisRequest(BaseModel):
    """Jurisdiction analysis request schema."""
    document_id: str = Field(..., description="Document ID to analyze")
    force_jurisdiction: Optional[JurisdictionType] = Field(None, description="Force specific jurisdiction")
    analysis_options: Dict[str, Any] = Field(default_factory=dict, description="Analysis options")


class StampDutyCalculation(BaseModel):
    """Stamp duty calculation schema."""
    state: str = Field(..., description="Indian state")
    document_type: str = Field(..., description="Document type")
    value: float = Field(..., ge=0, description="Document value")
    stamp_duty_amount: float = Field(..., ge=0, description="Calculated stamp duty")
    registration_fee: Optional[float] = Field(None, ge=0, description="Registration fee if applicable")
    total_cost: float = Field(..., ge=0, description="Total cost")
    calculation_details: Dict[str, Any] = Field(..., description="Calculation breakdown")


class ComplianceCheckItem(BaseModel):
    """Compliance check item schema."""
    requirement: str = Field(..., description="Compliance requirement")
    status: str = Field(..., description="Compliance status")
    description: str = Field(..., description="Requirement description")
    action_required: Optional[str] = Field(None, description="Action required if non-compliant")
    priority: str = Field(..., description="Priority level")


class JurisdictionComparisonResponse(BaseModel):
    """Jurisdiction comparison response schema."""
    document_id: str = Field(..., description="Document ID")
    
    # Comparison results
    enforceability: Dict[str, Any] = Field(..., description="Enforceability comparison")
    formalities: Dict[str, Any] = Field(..., description="Formalities comparison")
    costs: Dict[str, Any] = Field(..., description="Cost comparison")
    timeline: Dict[str, Any] = Field(..., description="Timeline comparison")
    risks: Dict[str, Any] = Field(..., description="Risk comparison")
    
    # Recommendations
    recommended_jurisdiction: str = Field(..., description="Recommended jurisdiction")
    reasoning: str = Field(..., description="Reasoning for recommendation")
    alternative_options: List[Dict[str, Any]] = Field(..., description="Alternative options")
    
    created_at: datetime = Field(..., description="Creation timestamp")