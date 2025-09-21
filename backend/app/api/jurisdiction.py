"""
Jurisdiction-specific API endpoints.

Provides endpoints for jurisdiction detection, Indian legal analysis, US legal analysis,
cross-border comparison, and stamp duty calculation.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import get_current_user
from ..database import get_db
from ..core.jurisdiction.detector import JurisdictionDetector, Jurisdiction
from ..core.jurisdiction.indian_processor import IndianLegalProcessor, IndianState
from ..core.jurisdiction.us_processor import USLegalProcessor, USState
from ..core.jurisdiction.comparative_analyzer import ComparativeJurisdictionAnalyzer
from ..schemas.jurisdiction import (
    JurisdictionDetectionResponse,
    IndianLegalAnalysis as IndianLegalAnalysisSchema,
    USLegalAnalysis as USLegalAnalysisSchema,
    StampDutyCalculation,
    JurisdictionComparisonResponse,
    JurisdictionType
)
from ..services.document_service import DocumentService
from ..database.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jurisdiction")

# Initialize jurisdiction processors
jurisdiction_detector = JurisdictionDetector()
indian_processor = IndianLegalProcessor()
us_processor = USLegalProcessor()
comparative_analyzer = ComparativeJurisdictionAnalyzer()


async def get_document_content_text(db: AsyncSession, document_id: str, current_user: User) -> str:
    """Helper function to get document content as text."""
    document = await DocumentService.get_document_by_id(db, document_id, current_user)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get document content from file
    document_content = await DocumentService.get_document_content(document)
    if not document_content:
        raise HTTPException(status_code=400, detail="Document content not available")
    
    # Convert bytes to string if needed
    if isinstance(document_content, bytes):
        try:
            return document_content.decode('utf-8')
        except UnicodeDecodeError:
            # Try with different encoding
            return document_content.decode('latin-1')
    
    return str(document_content)


@router.post("/detect", response_model=JurisdictionDetectionResponse)
async def detect_jurisdiction(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Automatically detect jurisdiction of a legal document.
    
    Analyzes document content to determine whether it's an Indian, US, or cross-border
    legal document with confidence scoring and detected elements.
    """
    try:
        # Get document content
        document_content = await get_document_content_text(db, document_id, current_user)
        
        # Perform jurisdiction detection
        result = jurisdiction_detector.detect_jurisdiction(document_content)
        
        # Map jurisdiction enum to schema enum
        jurisdiction_mapping = {
            Jurisdiction.INDIA: JurisdictionType.INDIA,
            Jurisdiction.USA: JurisdictionType.USA,
            Jurisdiction.CROSS_BORDER: JurisdictionType.CROSS_BORDER,
            Jurisdiction.UNKNOWN: JurisdictionType.USA  # Default fallback
        }
        
        return JurisdictionDetectionResponse(
            jurisdiction=jurisdiction_mapping.get(result.jurisdiction, JurisdictionType.USA),
            confidence=result.confidence,
            scores=result.scores,
            us_state=result.us_state,
            detected_elements=result.detected_elements
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting jurisdiction for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect jurisdiction")


@router.post("/india/analyze", response_model=IndianLegalAnalysisSchema)
async def analyze_indian_legal_document(
    document_id: str,
    state: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform comprehensive Indian legal analysis of a document.
    
    Analyzes document for Indian legal acts, stamp duty requirements, GST implications,
    registration requirements, and compliance checklist.
    """
    try:
        # Get document content
        document_content = await get_document_content_text(db, document_id, current_user)
        
        # Convert state string to enum if provided
        indian_state = None
        if state:
            try:
                # Try to find matching state enum
                for state_enum in IndianState:
                    if state_enum.value.lower() == state.lower():
                        indian_state = state_enum
                        break
            except Exception:
                logger.warning(f"Invalid Indian state provided: {state}")
        
        # Perform Indian legal analysis
        analysis = indian_processor.analyze_document(document_content, indian_state)
        
        # Convert to schema format
        return IndianLegalAnalysisSchema(
            applicable_acts=[
                {
                    "act_name": ref.act_name,
                    "full_name": ref.full_name,
                    "year": ref.year,
                    "sections": ref.sections,
                    "confidence": ref.confidence,
                    "context": ref.context
                }
                for ref in analysis.act_references
            ],
            stamp_duty={
                "state": analysis.stamp_duty.state.value,
                "document_type": analysis.stamp_duty.document_type.value,
                "consideration_amount": float(analysis.stamp_duty.consideration_amount) if analysis.stamp_duty.consideration_amount else None,
                "stamp_duty_rate": analysis.stamp_duty.stamp_duty_rate,
                "calculated_duty": float(analysis.stamp_duty.calculated_duty) if analysis.stamp_duty.calculated_duty else None,
                "minimum_duty": float(analysis.stamp_duty.minimum_duty),
                "maximum_duty": float(analysis.stamp_duty.maximum_duty) if analysis.stamp_duty.maximum_duty else None,
                "exemptions": analysis.stamp_duty.exemptions,
                "requirements": analysis.stamp_duty.requirements,
                "compliance_status": analysis.stamp_duty.compliance_status
            },
            gst_implications={
                "applicable": analysis.gst_analysis.applicable,
                "gst_rate": analysis.gst_analysis.gst_rate,
                "hsn_codes": analysis.gst_analysis.hsn_codes,
                "place_of_supply": analysis.gst_analysis.place_of_supply,
                "reverse_charge": analysis.gst_analysis.reverse_charge,
                "exemptions": analysis.gst_analysis.exemptions,
                "compliance_requirements": analysis.gst_analysis.compliance_requirements,
                "registration_required": analysis.gst_analysis.registration_required
            },
            registration_requirements=[
                {
                    "required": req.required,
                    "authority": req.authority,
                    "time_limit": req.time_limit,
                    "fees": float(req.fees) if req.fees else None,
                    "documents_needed": req.documents_needed,
                    "consequences_of_non_registration": req.consequences_of_non_registration
                }
                for req in analysis.registration_requirements
            ],
            compliance_checklist=[
                {
                    "compliant": analysis.compliance_check.compliant,
                    "violations": analysis.compliance_check.violations,
                    "recommendations": analysis.compliance_check.recommendations,
                    "mandatory_clauses": analysis.compliance_check.mandatory_clauses,
                    "missing_clauses": analysis.compliance_check.missing_clauses,
                    "risk_level": analysis.compliance_check.risk_level
                }
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing Indian legal document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze Indian legal document")


@router.post("/usa/analyze", response_model=USLegalAnalysisSchema)
async def analyze_us_legal_document(
    document_id: str,
    state: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform comprehensive US legal analysis of a document.
    
    Analyzes document for federal regulations, state law applicability, UCC compliance,
    securities law compliance, and privacy law compliance.
    """
    try:
        # Get document content
        document_content = await get_document_content_text(db, document_id, current_user)
        
        # Convert state string to enum if provided
        us_state = None
        if state:
            try:
                # Try to find matching state enum
                for state_enum in USState:
                    if state_enum.value.lower() == state.lower():
                        us_state = state_enum
                        break
            except Exception:
                logger.warning(f"Invalid US state provided: {state}")
        
        # Perform US legal analysis
        analysis = us_processor.analyze_document(document_content, us_state)
        
        # Convert to schema format
        return USLegalAnalysisSchema(
            federal_regulations=[
                {
                    "law_name": ref.law_name,
                    "full_name": ref.full_name,
                    "citation": ref.citation,
                    "sections": ref.sections,
                    "confidence": ref.confidence,
                    "context": ref.context
                }
                for ref in analysis.federal_references
            ],
            state_jurisdiction=analysis.state_jurisdiction.governing_state.value if analysis.state_jurisdiction.governing_state else None,
            ucc_analysis={
                "applicable": analysis.ucc_analysis.applicable,
                "articles": analysis.ucc_analysis.articles,
                "transaction_type": analysis.ucc_analysis.transaction_type,
                "state_variations": analysis.ucc_analysis.state_variations,
                "compliance_requirements": analysis.ucc_analysis.compliance_requirements,
                "risk_factors": analysis.ucc_analysis.risk_factors,
                "recommendations": analysis.ucc_analysis.recommendations
            },
            securities_compliance={
                "securities_involved": analysis.securities_analysis.securities_involved,
                "federal_exemptions": analysis.securities_analysis.federal_exemptions,
                "state_exemptions": analysis.securities_analysis.state_exemptions,
                "registration_requirements": analysis.securities_analysis.registration_requirements,
                "disclosure_requirements": analysis.securities_analysis.disclosure_requirements,
                "compliance_status": analysis.securities_analysis.compliance_status,
                "risk_level": analysis.securities_analysis.risk_level
            },
            privacy_compliance={
                "applicable_laws": analysis.privacy_analysis.applicable_laws,
                "data_types_processed": analysis.privacy_analysis.data_types_processed,
                "consent_requirements": analysis.privacy_analysis.consent_requirements,
                "disclosure_requirements": analysis.privacy_analysis.disclosure_requirements,
                "user_rights": analysis.privacy_analysis.user_rights,
                "compliance_gaps": analysis.privacy_analysis.compliance_gaps,
                "recommendations": analysis.privacy_analysis.recommendations
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing US legal document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze US legal document")


@router.post("/compare", response_model=JurisdictionComparisonResponse)
async def compare_jurisdictions(
    document_id: str,
    indian_state: Optional[str] = None,
    us_state: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform cross-border comparison between Indian and US legal requirements.
    
    Analyzes enforceability, formalities, costs, timelines, and risks across jurisdictions
    and provides recommendations for cross-border transactions.
    """
    try:
        # Get document content
        document_content = await get_document_content_text(db, document_id, current_user)
        
        # Convert state strings to enums if provided
        indian_state_enum = None
        if indian_state:
            try:
                for state_enum in IndianState:
                    if state_enum.value.lower() == indian_state.lower():
                        indian_state_enum = state_enum
                        break
            except Exception:
                logger.warning(f"Invalid Indian state provided: {indian_state}")
        
        us_state_enum = None
        if us_state:
            try:
                for state_enum in USState:
                    if state_enum.value.lower() == us_state.lower():
                        us_state_enum = state_enum
                        break
            except Exception:
                logger.warning(f"Invalid US state provided: {us_state}")
        
        # Perform cross-border analysis
        analysis = comparative_analyzer.analyze_cross_border_document(
            document_content, indian_state_enum, us_state_enum
        )
        
        # Get document for metadata
        document = await DocumentService.get_document_by_id(db, document_id, current_user)
        
        # Convert to schema format
        return JurisdictionComparisonResponse(
            document_id=document_id,
            enforceability={
                "india_enforceability": analysis.enforceability_comparison.india_enforceability,
                "us_enforceability": analysis.enforceability_comparison.us_enforceability,
                "cross_border_risks": analysis.enforceability_comparison.cross_border_risks,
                "enforceability_score": analysis.enforceability_comparison.enforceability_score,
                "risk_level": analysis.enforceability_comparison.risk_level.value
            },
            formalities={
                "stamp_duty_comparison": analysis.formalities_comparison.stamp_duty_comparison,
                "registration_comparison": analysis.formalities_comparison.registration_comparison,
                "witness_requirements": analysis.formalities_comparison.witness_requirements,
                "notarization_requirements": analysis.formalities_comparison.notarization_requirements,
                "execution_formalities": analysis.formalities_comparison.execution_formalities,
                "compliance_gaps": analysis.formalities_comparison.compliance_gaps
            },
            costs={
                "india_costs": {
                    "stamp_duty": analysis.formalities_comparison.stamp_duty_comparison.get("india", {}),
                    "registration_fees": analysis.formalities_comparison.registration_comparison.get("india", {}),
                    "legal_fees": "Varies by complexity and location"
                },
                "us_costs": {
                    "filing_fees": analysis.formalities_comparison.registration_comparison.get("us", {}),
                    "legal_fees": "Varies by state and complexity",
                    "recording_fees": "Varies by state and document type"
                }
            },
            timeline={
                "india_timeline": {
                    "execution": "1-2 days",
                    "registration": "4 months from execution",
                    "enforcement": "2-5 years (varies by court)"
                },
                "us_timeline": {
                    "execution": "Same day possible",
                    "filing": "Varies by state",
                    "enforcement": "6 months - 2 years (varies by state)"
                }
            },
            risks={
                "enforceability_risks": analysis.enforceability_comparison.cross_border_risks,
                "compliance_gaps": [
                    {
                        "gap_type": gap.gap_type.value,
                        "description": gap.description,
                        "india_requirement": gap.india_requirement,
                        "us_requirement": gap.us_requirement,
                        "impact": gap.impact,
                        "mitigation_strategy": gap.mitigation_strategy,
                        "priority": gap.priority
                    }
                    for gap in analysis.compliance_gaps
                ],
                "overall_risk": analysis.overall_risk_assessment
            },
            recommended_jurisdiction=analysis.recommended_governing_law,
            reasoning=f"Based on analysis of enforceability ({analysis.enforceability_comparison.risk_level.value} risk), formalities, and tax implications",
            alternative_options=[
                {
                    "jurisdiction": "Singapore Law",
                    "pros": ["Neutral jurisdiction", "International arbitration friendly", "English common law based"],
                    "cons": ["Higher legal costs", "Less familiar to parties"]
                },
                {
                    "jurisdiction": "English Law",
                    "pros": ["Well-developed commercial law", "International recognition", "Arbitration friendly"],
                    "cons": ["Higher legal costs", "Brexit implications"]
                }
            ],
            created_at=document.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing jurisdictions for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare jurisdictions")


@router.post("/india/stamp-duty", response_model=StampDutyCalculation)
async def calculate_stamp_duty(
    document_id: str,
    state: str,
    document_type: str,
    value: float,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate stamp duty for Indian legal documents.
    
    Calculates stamp duty based on state, document type, and document value,
    including registration fees and total costs.
    """
    try:
        # Validate inputs
        if value < 0:
            raise HTTPException(status_code=400, detail="Document value must be non-negative")
        
        # Convert state string to enum
        indian_state = None
        try:
            for state_enum in IndianState:
                if state_enum.value.lower() == state.lower():
                    indian_state = state_enum
                    break
            if not indian_state:
                raise ValueError(f"Invalid state: {state}")
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid Indian state: {state}")
        
        # Get document for context (optional)
        try:
            document_content = await get_document_content_text(db, document_id, current_user)
        except:
            document_content = ""
        
        # Perform stamp duty calculation using Indian processor
        from ..core.jurisdiction.indian_processor import DocumentType
        
        # Convert document type string to enum
        doc_type = None
        try:
            for dt in DocumentType:
                if dt.value.lower() == document_type.lower():
                    doc_type = dt
                    break
            if not doc_type:
                doc_type = DocumentType.AGREEMENT  # Default fallback
        except Exception:
            doc_type = DocumentType.AGREEMENT
        
        # Calculate stamp duty using the processor's internal method
        from decimal import Decimal
        consideration = Decimal(str(value))
        
        # Get stamp duty rates for the state and document type
        state_rates = indian_processor.stamp_duty_rates.get(
            indian_state, 
            indian_processor.stamp_duty_rates[IndianState.DELHI]
        )
        duty_info = state_rates.get(doc_type, state_rates[DocumentType.AGREEMENT])
        
        # Calculate duty
        rate = duty_info['rate']
        minimum_duty = Decimal(str(duty_info['minimum']))
        maximum_duty = Decimal(str(duty_info['maximum'])) if duty_info['maximum'] else None
        
        calculated_duty = consideration * Decimal(str(rate)) / Decimal('100')
        calculated_duty = max(calculated_duty, minimum_duty)
        if maximum_duty:
            calculated_duty = min(calculated_duty, maximum_duty)
        
        # Calculate registration fee (typically 1% of document value, minimum Rs. 500)
        registration_fee = max(consideration * Decimal('0.01'), Decimal('500'))
        
        # Total cost
        total_cost = calculated_duty + registration_fee
        
        return StampDutyCalculation(
            state=state,
            document_type=document_type,
            value=value,
            stamp_duty_amount=float(calculated_duty),
            registration_fee=float(registration_fee),
            total_cost=float(total_cost),
            calculation_details={
                "stamp_duty_rate": rate,
                "minimum_duty": float(minimum_duty),
                "maximum_duty": float(maximum_duty) if maximum_duty else None,
                "consideration_amount": value,
                "calculation_method": f"({value} * {rate}%) = {float(calculated_duty)}, minimum {float(minimum_duty)}",
                "registration_fee_calculation": f"max({value} * 1%, 500) = {float(registration_fee)}",
                "applicable_exemptions": [],
                "notes": [
                    "Stamp duty rates vary by state and document type",
                    "Registration is mandatory for documents above certain value",
                    "Penalties apply for insufficient stamp duty"
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating stamp duty: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate stamp duty")


@router.get("/templates/{jurisdiction}/{document_type}")
async def get_document_template(
    jurisdiction: str,
    document_type: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get jurisdiction-specific document templates.
    
    Provides pre-built templates for common legal documents based on jurisdiction
    and document type, including required clauses and formatting.
    """
    try:
        # Validate jurisdiction
        valid_jurisdictions = ["india", "usa", "cross-border"]
        if jurisdiction.lower() not in valid_jurisdictions:
            raise HTTPException(status_code=400, detail=f"Invalid jurisdiction. Must be one of: {valid_jurisdictions}")
        
        # Define template data structure
        templates = {
            "india": {
                "agreement": {
                    "name": "Indian Agreement Template",
                    "description": "Standard agreement template compliant with Indian Contract Act, 2013",
                    "required_clauses": [
                        "Parties identification with complete address",
                        "Consideration clause with amount in words and figures",
                        "Terms and conditions",
                        "Governing law clause (Indian law)",
                        "Jurisdiction clause (Indian courts)",
                        "Stamp duty compliance statement",
                        "Registration requirements",
                        "Witness signatures (minimum 2)"
                    ],
                    "optional_clauses": [
                        "Arbitration clause",
                        "Force majeure clause",
                        "Confidentiality clause",
                        "Termination clause"
                    ],
                    "compliance_requirements": [
                        "Stamp duty payment as per state rates",
                        "Registration within 4 months if value > Rs. 100",
                        "GST compliance if applicable",
                        "Foreign exchange compliance if foreign party involved"
                    ],
                    "template_sections": [
                        {
                            "section": "Header",
                            "content": "AGREEMENT\n\nThis Agreement is made on [DATE] between:\n\nPARTY 1: [NAME], [DESIGNATION], having its [registered office/residence] at [ADDRESS] (hereinafter referred to as \"[PARTY1_TERM]\")\n\nAND\n\nPARTY 2: [NAME], [DESIGNATION], having its [registered office/residence] at [ADDRESS] (hereinafter referred to as \"[PARTY2_TERM]\")"
                        },
                        {
                            "section": "Recitals",
                            "content": "WHEREAS [BACKGROUND_CLAUSE_1];\n\nWHEREAS [BACKGROUND_CLAUSE_2];\n\nNOW THEREFORE, in consideration of the mutual covenants and agreements contained herein, the parties agree as follows:"
                        },
                        {
                            "section": "Terms",
                            "content": "1. [MAIN_OBLIGATION_1]\n\n2. [MAIN_OBLIGATION_2]\n\n3. CONSIDERATION: The consideration for this agreement is Rs. [AMOUNT] ([AMOUNT_IN_WORDS]).\n\n4. GOVERNING LAW: This Agreement shall be governed by and construed in accordance with the laws of India.\n\n5. JURISDICTION: Any disputes arising out of this Agreement shall be subject to the exclusive jurisdiction of courts in [CITY], [STATE]."
                        },
                        {
                            "section": "Footer",
                            "content": "IN WITNESS WHEREOF, the parties have executed this Agreement on the date first written above.\n\n[PARTY1_NAME]                    [PARTY2_NAME]\n(Party 1)                        (Party 2)\n\nWitness 1:                       Witness 2:\n[NAME]                           [NAME]\n[ADDRESS]                        [ADDRESS]\n[SIGNATURE]                      [SIGNATURE]"
                        }
                    ]
                },
                "sale_deed": {
                    "name": "Indian Sale Deed Template",
                    "description": "Sale deed template compliant with Transfer of Property Act, 1882",
                    "required_clauses": [
                        "Vendor and purchaser details",
                        "Property description with survey numbers",
                        "Sale consideration",
                        "Title verification clause",
                        "Possession delivery clause",
                        "Registration clause",
                        "Stamp duty payment clause"
                    ],
                    "compliance_requirements": [
                        "Stamp duty as per state rates (typically 5-10% of property value)",
                        "Registration mandatory",
                        "Title verification required",
                        "Encumbrance certificate required"
                    ]
                },
                "employment": {
                    "name": "Indian Employment Agreement Template",
                    "description": "Employment contract compliant with Indian labor laws",
                    "required_clauses": [
                        "Employee and employer details",
                        "Job description and responsibilities",
                        "Salary and benefits",
                        "Working hours and leave policy",
                        "Termination clause",
                        "Confidentiality and non-compete",
                        "Compliance with labor laws"
                    ],
                    "compliance_requirements": [
                        "Compliance with Minimum Wages Act",
                        "ESI and EPF registration if applicable",
                        "Contract Labor Act compliance",
                        "Shop and Establishment Act registration"
                    ]
                }
            },
            "usa": {
                "agreement": {
                    "name": "US Agreement Template",
                    "description": "Standard agreement template compliant with US contract law",
                    "required_clauses": [
                        "Parties identification",
                        "Consideration clause",
                        "Terms and conditions",
                        "Governing law clause",
                        "Jurisdiction/venue clause",
                        "Entire agreement clause",
                        "Severability clause",
                        "Signature block"
                    ],
                    "optional_clauses": [
                        "Arbitration clause",
                        "Force majeure clause",
                        "Confidentiality clause",
                        "Limitation of liability",
                        "Indemnification clause"
                    ],
                    "compliance_requirements": [
                        "Statute of frauds compliance for contracts over $500",
                        "UCC compliance for sale of goods",
                        "State-specific requirements",
                        "Securities law compliance if applicable"
                    ],
                    "template_sections": [
                        {
                            "section": "Header",
                            "content": "AGREEMENT\n\nThis Agreement is entered into on [DATE] by and between:\n\n[PARTY1_NAME], a [STATE] [ENTITY_TYPE] (\"[PARTY1_TERM]\")\n\nand\n\n[PARTY2_NAME], a [STATE] [ENTITY_TYPE] (\"[PARTY2_TERM]\")"
                        },
                        {
                            "section": "Recitals",
                            "content": "WHEREAS, [RECITAL_1];\n\nWHEREAS, [RECITAL_2];\n\nNOW, THEREFORE, in consideration of the mutual covenants contained herein and for other good and valuable consideration, the parties agree as follows:"
                        },
                        {
                            "section": "Terms",
                            "content": "1. [MAIN_TERM_1]\n\n2. [MAIN_TERM_2]\n\n3. Consideration. The consideration for this Agreement is $[AMOUNT].\n\n4. Governing Law. This Agreement shall be governed by the laws of the State of [STATE].\n\n5. Jurisdiction. Any legal action arising out of this Agreement shall be brought in the courts of [STATE]."
                        },
                        {
                            "section": "Footer",
                            "content": "IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.\n\n[PARTY1_NAME]                    [PARTY2_NAME]\n\nBy: _________________________    By: _________________________\nName: [NAME]                     Name: [NAME]\nTitle: [TITLE]                   Title: [TITLE]"
                        }
                    ]
                },
                "purchase_agreement": {
                    "name": "US Purchase Agreement Template",
                    "description": "Asset purchase agreement template compliant with US commercial law",
                    "required_clauses": [
                        "Asset description",
                        "Purchase price",
                        "Closing conditions",
                        "Representations and warranties",
                        "Indemnification",
                        "UCC compliance statements"
                    ],
                    "compliance_requirements": [
                        "UCC Article 2 compliance for goods",
                        "Securities law compliance if applicable",
                        "State filing requirements",
                        "Tax compliance"
                    ]
                },
                "employment": {
                    "name": "US Employment Agreement Template",
                    "description": "Employment contract compliant with US labor laws",
                    "required_clauses": [
                        "At-will employment clause",
                        "Job description",
                        "Compensation and benefits",
                        "Confidentiality agreement",
                        "Non-compete clause (where permitted)",
                        "Equal opportunity statement"
                    ],
                    "compliance_requirements": [
                        "Fair Labor Standards Act compliance",
                        "State-specific employment law compliance",
                        "I-9 employment eligibility verification",
                        "Workers' compensation coverage"
                    ]
                }
            },
            "cross-border": {
                "international_agreement": {
                    "name": "Cross-Border Agreement Template",
                    "description": "International agreement template for India-US transactions",
                    "required_clauses": [
                        "Parties with complete addresses and jurisdictions",
                        "Governing law clause (recommended: neutral jurisdiction)",
                        "Dispute resolution clause (arbitration recommended)",
                        "Currency and payment terms",
                        "Force majeure clause",
                        "Compliance with both jurisdictions",
                        "Tax implications clause",
                        "Foreign exchange compliance"
                    ],
                    "compliance_requirements": [
                        "FEMA compliance (India)",
                        "US tax reporting requirements",
                        "Transfer pricing compliance",
                        "Anti-money laundering compliance",
                        "Sanctions compliance"
                    ],
                    "recommended_governing_law": "Singapore Law or English Law",
                    "recommended_arbitration": "Singapore International Arbitration Centre (SIAC) or London Court of International Arbitration (LCIA)"
                }
            }
        }
        
        # Get template for requested jurisdiction and document type
        jurisdiction_templates = templates.get(jurisdiction.lower())
        if not jurisdiction_templates:
            raise HTTPException(status_code=404, detail=f"No templates available for jurisdiction: {jurisdiction}")
        
        template = jurisdiction_templates.get(document_type.lower())
        if not template:
            available_types = list(jurisdiction_templates.keys())
            raise HTTPException(
                status_code=404, 
                detail=f"Document type '{document_type}' not found for {jurisdiction}. Available types: {available_types}"
            )
        
        return {
            "jurisdiction": jurisdiction.lower(),
            "document_type": document_type.lower(),
            "template": template,
            "metadata": {
                "created_at": "2024-01-01T00:00:00Z",
                "version": "1.0",
                "last_updated": "2024-01-01T00:00:00Z"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving template for {jurisdiction}/{document_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve document template")


@router.get("/compliance-checklist")
async def get_compliance_checklist(
    jurisdiction: str,
    document_type: str,
    state: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get jurisdiction-specific compliance checklist.
    
    Provides comprehensive compliance requirements for legal documents
    based on jurisdiction, document type, and state (if applicable).
    """
    try:
        # Validate jurisdiction
        valid_jurisdictions = ["india", "usa", "cross-border"]
        if jurisdiction.lower() not in valid_jurisdictions:
            raise HTTPException(status_code=400, detail=f"Invalid jurisdiction. Must be one of: {valid_jurisdictions}")
        
        # Define compliance checklists
        compliance_data = {
            "india": {
                "agreement": {
                    "pre_execution": [
                        {
                            "item": "Verify parties' legal capacity",
                            "description": "Ensure all parties have legal capacity to enter into contract",
                            "mandatory": True,
                            "penalty": "Contract may be voidable"
                        },
                        {
                            "item": "Determine stamp duty liability",
                            "description": "Calculate stamp duty based on state rates and document value",
                            "mandatory": True,
                            "penalty": "10x stamp duty + penalty"
                        },
                        {
                            "item": "Check registration requirements",
                            "description": "Determine if document requires registration",
                            "mandatory": True,
                            "penalty": "Document not admissible in court"
                        }
                    ],
                    "execution": [
                        {
                            "item": "Use proper stamp paper or e-stamping",
                            "description": "Execute on stamp paper of correct value",
                            "mandatory": True,
                            "penalty": "Document inadmissible"
                        },
                        {
                            "item": "Obtain witness signatures",
                            "description": "Minimum 2 witnesses required",
                            "mandatory": True,
                            "penalty": "Difficulty in proving execution"
                        },
                        {
                            "item": "Date and place of execution",
                            "description": "Clearly mention date and place of execution",
                            "mandatory": True,
                            "penalty": "Ambiguity in legal proceedings"
                        }
                    ],
                    "post_execution": [
                        {
                            "item": "Register document if required",
                            "description": "Register within 4 months of execution",
                            "mandatory": True,
                            "penalty": "Document not admissible + penalty"
                        },
                        {
                            "item": "GST compliance if applicable",
                            "description": "Pay GST if transaction attracts GST",
                            "mandatory": True,
                            "penalty": "GST penalty + interest"
                        },
                        {
                            "item": "Maintain records",
                            "description": "Keep copies and receipts for future reference",
                            "mandatory": True,
                            "penalty": "Difficulty in enforcement"
                        }
                    ]
                },
                "sale_deed": {
                    "pre_execution": [
                        {
                            "item": "Title verification",
                            "description": "Verify clear and marketable title of property",
                            "mandatory": True,
                            "penalty": "Risk of title disputes"
                        },
                        {
                            "item": "Encumbrance certificate",
                            "description": "Obtain 30-year encumbrance certificate",
                            "mandatory": True,
                            "penalty": "Hidden liabilities"
                        },
                        {
                            "item": "Property valuation",
                            "description": "Get property valued for stamp duty calculation",
                            "mandatory": True,
                            "penalty": "Incorrect stamp duty payment"
                        }
                    ],
                    "execution": [
                        {
                            "item": "Stamp duty payment",
                            "description": "Pay stamp duty as per state rates (5-10% of value)",
                            "mandatory": True,
                            "penalty": "10x penalty + document inadmissible"
                        },
                        {
                            "item": "Registration",
                            "description": "Register sale deed with sub-registrar",
                            "mandatory": True,
                            "penalty": "Transfer not legally valid"
                        }
                    ]
                }
            },
            "usa": {
                "agreement": {
                    "pre_execution": [
                        {
                            "item": "Authority verification",
                            "description": "Verify signatory authority for corporate parties",
                            "mandatory": True,
                            "penalty": "Contract may be unenforceable"
                        },
                        {
                            "item": "Statute of frauds compliance",
                            "description": "Written agreement required for contracts over $500 or lasting over 1 year",
                            "mandatory": True,
                            "penalty": "Contract unenforceable"
                        },
                        {
                            "item": "UCC applicability check",
                            "description": "Determine if UCC Article 2 applies to goods transactions",
                            "mandatory": True,
                            "penalty": "Incorrect legal framework applied"
                        }
                    ],
                    "execution": [
                        {
                            "item": "Proper execution",
                            "description": "Ensure proper signatures and dating",
                            "mandatory": True,
                            "penalty": "Questions about validity"
                        },
                        {
                            "item": "Notarization if required",
                            "description": "Notarize if required by state law",
                            "mandatory": False,
                            "penalty": "May affect enforceability"
                        }
                    ],
                    "post_execution": [
                        {
                            "item": "Filing requirements",
                            "description": "File with appropriate state agencies if required",
                            "mandatory": False,
                            "penalty": "May affect third-party rights"
                        },
                        {
                            "item": "Tax compliance",
                            "description": "Report transaction for tax purposes if required",
                            "mandatory": True,
                            "penalty": "Tax penalties"
                        }
                    ]
                },
                "employment": {
                    "pre_execution": [
                        {
                            "item": "I-9 verification",
                            "description": "Verify employment eligibility",
                            "mandatory": True,
                            "penalty": "Federal penalties"
                        },
                        {
                            "item": "Background checks",
                            "description": "Conduct permissible background checks",
                            "mandatory": False,
                            "penalty": "Hiring risks"
                        }
                    ],
                    "execution": [
                        {
                            "item": "At-will employment clause",
                            "description": "Include at-will employment language where permitted",
                            "mandatory": False,
                            "penalty": "Wrongful termination claims"
                        },
                        {
                            "item": "Equal opportunity compliance",
                            "description": "Include EEO statements",
                            "mandatory": True,
                            "penalty": "Discrimination claims"
                        }
                    ]
                }
            },
            "cross-border": {
                "international_agreement": {
                    "pre_execution": [
                        {
                            "item": "FEMA compliance check (India)",
                            "description": "Verify compliance with Foreign Exchange Management Act",
                            "mandatory": True,
                            "penalty": "FEMA violations and penalties"
                        },
                        {
                            "item": "US sanctions compliance",
                            "description": "Check OFAC and other sanctions lists",
                            "mandatory": True,
                            "penalty": "Criminal and civil penalties"
                        },
                        {
                            "item": "Tax treaty benefits analysis",
                            "description": "Analyze India-US DTAA benefits",
                            "mandatory": False,
                            "penalty": "Higher tax burden"
                        }
                    ],
                    "execution": [
                        {
                            "item": "Governing law clause",
                            "description": "Choose neutral governing law (Singapore/English law recommended)",
                            "mandatory": True,
                            "penalty": "Jurisdictional conflicts"
                        },
                        {
                            "item": "Arbitration clause",
                            "description": "Include international arbitration clause",
                            "mandatory": False,
                            "penalty": "Complex litigation in multiple jurisdictions"
                        },
                        {
                            "item": "Currency and payment terms",
                            "description": "Specify currency and payment mechanisms",
                            "mandatory": True,
                            "penalty": "Payment disputes"
                        }
                    ],
                    "post_execution": [
                        {
                            "item": "RBI reporting (India)",
                            "description": "Report foreign exchange transactions to RBI",
                            "mandatory": True,
                            "penalty": "FEMA penalties"
                        },
                        {
                            "item": "US tax reporting",
                            "description": "Report foreign transactions if required",
                            "mandatory": True,
                            "penalty": "IRS penalties"
                        },
                        {
                            "item": "Transfer pricing documentation",
                            "description": "Maintain transfer pricing documentation",
                            "mandatory": True,
                            "penalty": "Tax adjustments and penalties"
                        }
                    ]
                }
            }
        }
        
        # Get compliance checklist
        jurisdiction_data = compliance_data.get(jurisdiction.lower())
        if not jurisdiction_data:
            raise HTTPException(status_code=404, detail=f"No compliance data available for jurisdiction: {jurisdiction}")
        
        checklist = jurisdiction_data.get(document_type.lower())
        if not checklist:
            available_types = list(jurisdiction_data.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Document type '{document_type}' not found for {jurisdiction}. Available types: {available_types}"
            )
        
        # Add state-specific requirements if applicable
        state_specific = {}
        if jurisdiction.lower() == "india" and state:
            state_specific = {
                "stamp_duty_rates": f"Stamp duty rates vary by state. For {state}, consult local stamp duty schedule.",
                "registration_fees": f"Registration fees in {state} are typically 1% of document value.",
                "local_requirements": f"Check {state}-specific requirements for additional compliance."
            }
        elif jurisdiction.lower() == "usa" and state:
            state_specific = {
                "state_law_requirements": f"{state} may have specific requirements for this document type.",
                "filing_requirements": f"Check {state} Secretary of State filing requirements if applicable.",
                "notarization": f"{state} notarization requirements may apply."
            }
        
        return {
            "jurisdiction": jurisdiction.lower(),
            "document_type": document_type.lower(),
            "state": state,
            "checklist": checklist,
            "state_specific_requirements": state_specific,
            "metadata": {
                "total_items": sum(len(phase) for phase in checklist.values()),
                "mandatory_items": sum(
                    len([item for item in phase if item.get("mandatory", False)]) 
                    for phase in checklist.values()
                ),
                "last_updated": "2024-01-01T00:00:00Z"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving compliance checklist for {jurisdiction}/{document_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve compliance checklist")


@router.get("/legal-references/{jurisdiction}")
async def get_legal_references(
    jurisdiction: str,
    category: Optional[str] = None,
    search_term: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get jurisdiction-specific legal references.
    
    Provides access to relevant legal acts, regulations, and statutory provisions
    for Indian and US jurisdictions.
    """
    try:
        # Validate jurisdiction
        valid_jurisdictions = ["india", "usa"]
        if jurisdiction.lower() not in valid_jurisdictions:
            raise HTTPException(status_code=400, detail=f"Invalid jurisdiction. Must be one of: {valid_jurisdictions}")
        
        # Define legal references database
        legal_references = {
            "india": {
                "contract_law": [
                    {
                        "act_name": "Indian Contract Act, 1872",
                        "sections": {
                            "Section 10": "What agreements are contracts",
                            "Section 23": "What consideration and objects are lawful",
                            "Section 73": "Compensation for loss or damage caused by breach of contract",
                            "Section 124": "Contract of indemnity defined"
                        },
                        "key_provisions": [
                            "Essential elements of a valid contract",
                            "Void and voidable contracts",
                            "Breach of contract and remedies",
                            "Specific performance"
                        ]
                    },
                    {
                        "act_name": "Specific Relief Act, 1963",
                        "sections": {
                            "Section 10": "Specific performance of contracts",
                            "Section 20": "When specific performance is enforceable"
                        },
                        "key_provisions": [
                            "Specific performance of contracts",
                            "Injunctions",
                            "Rectification of instruments"
                        ]
                    }
                ],
                "property_law": [
                    {
                        "act_name": "Transfer of Property Act, 1882",
                        "sections": {
                            "Section 54": "Sale defined",
                            "Section 58": "Mortgage defined",
                            "Section 105": "Lease defined"
                        },
                        "key_provisions": [
                            "Transfer of immovable property",
                            "Sale, mortgage, lease provisions",
                            "Rights and liabilities of parties"
                        ]
                    },
                    {
                        "act_name": "Registration Act, 1908",
                        "sections": {
                            "Section 17": "Documents of which registration is compulsory",
                            "Section 23": "Time for presenting documents"
                        },
                        "key_provisions": [
                            "Compulsory registration requirements",
                            "Time limits for registration",
                            "Effects of non-registration"
                        ]
                    }
                ],
                "corporate_law": [
                    {
                        "act_name": "Companies Act, 2013",
                        "sections": {
                            "Section 2(20)": "Company defined",
                            "Section 8": "Formation of companies with charitable objects",
                            "Section 149": "Company to have Board of Directors"
                        },
                        "key_provisions": [
                            "Company incorporation and management",
                            "Directors' duties and liabilities",
                            "Meetings and resolutions",
                            "Winding up provisions"
                        ]
                    }
                ],
                "tax_law": [
                    {
                        "act_name": "Central Goods and Services Tax Act, 2017",
                        "sections": {
                            "Section 9": "Levy and collection of tax",
                            "Section 16": "Eligibility and conditions for taking input tax credit"
                        },
                        "key_provisions": [
                            "GST levy and collection",
                            "Input tax credit",
                            "Registration requirements",
                            "Returns and payments"
                        ]
                    },
                    {
                        "act_name": "Income Tax Act, 1961",
                        "sections": {
                            "Section 4": "Charge of income-tax",
                            "Section 92C": "Computation of arm's length price"
                        },
                        "key_provisions": [
                            "Income tax computation",
                            "Transfer pricing provisions",
                            "Tax deduction at source",
                            "International taxation"
                        ]
                    }
                ],
                "foreign_exchange": [
                    {
                        "act_name": "Foreign Exchange Management Act, 1999",
                        "sections": {
                            "Section 3": "Dealing in foreign exchange",
                            "Section 5": "Holding of foreign exchange"
                        },
                        "key_provisions": [
                            "Foreign exchange transactions",
                            "Current and capital account transactions",
                            "Authorized dealers",
                            "Penalties for violations"
                        ]
                    }
                ]
            },
            "usa": {
                "contract_law": [
                    {
                        "act_name": "Uniform Commercial Code (UCC)",
                        "articles": {
                            "Article 1": "General Provisions",
                            "Article 2": "Sales",
                            "Article 9": "Secured Transactions"
                        },
                        "key_provisions": [
                            "Sale of goods provisions",
                            "Warranties and remedies",
                            "Secured transactions",
                            "Negotiable instruments"
                        ]
                    },
                    {
                        "act_name": "Restatement (Second) of Contracts",
                        "sections": {
                            "Section 1": "Contract Defined",
                            "Section 17": "Requirement of a Bargain",
                            "Section 90": "Promise Reasonably Inducing Action or Forbearance"
                        },
                        "key_provisions": [
                            "Contract formation",
                            "Consideration requirements",
                            "Promissory estoppel",
                            "Contract interpretation"
                        ]
                    }
                ],
                "corporate_law": [
                    {
                        "act_name": "Delaware General Corporation Law",
                        "sections": {
                            "Section 101": "Incorporators",
                            "Section 141": "Board of directors",
                            "Section 242": "Amendment of certificate of incorporation"
                        },
                        "key_provisions": [
                            "Corporate formation",
                            "Board of directors duties",
                            "Shareholder rights",
                            "Mergers and acquisitions"
                        ]
                    }
                ],
                "securities_law": [
                    {
                        "act_name": "Securities Act of 1933",
                        "sections": {
                            "Section 5": "Prohibitions relating to interstate commerce and the mails",
                            "Section 4": "Exempted transactions"
                        },
                        "key_provisions": [
                            "Securities registration requirements",
                            "Exemptions from registration",
                            "Disclosure requirements",
                            "Anti-fraud provisions"
                        ]
                    },
                    {
                        "act_name": "Securities Exchange Act of 1934",
                        "sections": {
                            "Section 10(b)": "Manipulative and deceptive devices",
                            "Section 16": "Directors, officers, and principal stockholders"
                        },
                        "key_provisions": [
                            "Continuous disclosure requirements",
                            "Insider trading prohibitions",
                            "Proxy regulations",
                            "Market manipulation prohibitions"
                        ]
                    }
                ],
                "employment_law": [
                    {
                        "act_name": "Fair Labor Standards Act",
                        "sections": {
                            "Section 6": "Minimum wage",
                            "Section 7": "Maximum hours"
                        },
                        "key_provisions": [
                            "Minimum wage requirements",
                            "Overtime pay provisions",
                            "Child labor restrictions",
                            "Record keeping requirements"
                        ]
                    },
                    {
                        "act_name": "Title VII of the Civil Rights Act of 1964",
                        "sections": {
                            "Section 703": "Unlawful employment practices",
                            "Section 704": "Other unlawful employment practices"
                        },
                        "key_provisions": [
                            "Prohibition of employment discrimination",
                            "Protected classes",
                            "Reasonable accommodation",
                            "Retaliation prohibitions"
                        ]
                    }
                ],
                "privacy_law": [
                    {
                        "act_name": "California Consumer Privacy Act (CCPA)",
                        "sections": {
                            "Section 1798.100": "Right to know about personal information collected",
                            "Section 1798.105": "Right to delete personal information"
                        },
                        "key_provisions": [
                            "Consumer privacy rights",
                            "Data collection disclosure",
                            "Right to deletion",
                            "Non-discrimination provisions"
                        ]
                    }
                ]
            }
        }
        
        # Get references for jurisdiction
        jurisdiction_refs = legal_references.get(jurisdiction.lower())
        if not jurisdiction_refs:
            raise HTTPException(status_code=404, detail=f"No legal references available for jurisdiction: {jurisdiction}")
        
        # Filter by category if specified
        if category:
            category_refs = jurisdiction_refs.get(category.lower())
            if not category_refs:
                available_categories = list(jurisdiction_refs.keys())
                raise HTTPException(
                    status_code=404,
                    detail=f"Category '{category}' not found. Available categories: {available_categories}"
                )
            result_refs = {category.lower(): category_refs}
        else:
            result_refs = jurisdiction_refs
        
        # Apply search filter if specified
        if search_term:
            filtered_refs = {}
            search_lower = search_term.lower()
            
            for cat, refs in result_refs.items():
                filtered_cat_refs = []
                for ref in refs:
                    # Search in act name, sections, and key provisions
                    if (search_lower in ref.get("act_name", "").lower() or
                        any(search_lower in str(section).lower() for section in ref.get("sections", {}).values()) or
                        any(search_lower in provision.lower() for provision in ref.get("key_provisions", []))):
                        filtered_cat_refs.append(ref)
                
                if filtered_cat_refs:
                    filtered_refs[cat] = filtered_cat_refs
            
            result_refs = filtered_refs
        
        return {
            "jurisdiction": jurisdiction.lower(),
            "category": category,
            "search_term": search_term,
            "references": result_refs,
            "metadata": {
                "total_categories": len(result_refs),
                "total_references": sum(len(refs) for refs in result_refs.values()),
                "available_categories": list(jurisdiction_refs.keys()) if not category else None,
                "last_updated": "2024-01-01T00:00:00Z"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving legal references for {jurisdiction}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve legal references")


@router.get("/case-law/{jurisdiction}")
async def get_case_law_precedents(
    jurisdiction: str,
    legal_area: Optional[str] = None,
    search_term: Optional[str] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get case law and precedents for jurisdiction-specific legal areas.
    
    Provides access to important case law precedents and judicial decisions
    relevant to contract law, property law, and other legal areas.
    """
    try:
        # Validate jurisdiction
        valid_jurisdictions = ["india", "usa"]
        if jurisdiction.lower() not in valid_jurisdictions:
            raise HTTPException(status_code=400, detail=f"Invalid jurisdiction. Must be one of: {valid_jurisdictions}")
        
        # Validate limit
        if limit < 1 or limit > 50:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 50")
        
        # Define case law database
        case_law_db = {
            "india": {
                "contract_law": [
                    {
                        "case_name": "Balfour v. Balfour",
                        "citation": "AIR 1919 KB 571",
                        "court": "King's Bench Division",
                        "year": 1919,
                        "legal_principle": "Domestic agreements are generally not intended to create legal relations",
                        "facts": "Husband promised to pay wife monthly allowance while he worked abroad",
                        "holding": "Agreement between spouses in normal matrimonial relationship not legally binding",
                        "relevance": "Intention to create legal relations in contracts",
                        "keywords": ["intention to create legal relations", "domestic agreements", "consideration"]
                    },
                    {
                        "case_name": "Carlill v. Carbolic Smoke Ball Co.",
                        "citation": "AIR 1893 1 QB 256",
                        "court": "Court of Appeal",
                        "year": 1893,
                        "legal_principle": "Unilateral contracts can be formed through performance of specified acts",
                        "facts": "Company advertised reward for anyone who caught flu after using their product",
                        "holding": "Advertisement constituted a valid offer capable of acceptance by performance",
                        "relevance": "Offer and acceptance in unilateral contracts",
                        "keywords": ["unilateral contract", "offer", "acceptance", "consideration"]
                    },
                    {
                        "case_name": "Mohori Bibee v. Dharmodas Ghose",
                        "citation": "AIR 1903 PC 114",
                        "court": "Privy Council",
                        "year": 1903,
                        "legal_principle": "Contracts with minors are void ab initio under Indian law",
                        "facts": "Minor mortgaged property to moneylender",
                        "holding": "Contract with minor is void and cannot be ratified even after attaining majority",
                        "relevance": "Capacity to contract - minors",
                        "keywords": ["minor", "capacity", "void contract", "ratification"]
                    }
                ],
                "property_law": [
                    {
                        "case_name": "Tulsi v. Certified Officer",
                        "citation": "AIR 1985 SC 1416",
                        "court": "Supreme Court of India",
                        "year": 1985,
                        "legal_principle": "Registration is mandatory for documents affecting immovable property rights",
                        "facts": "Dispute over validity of unregistered sale deed",
                        "holding": "Unregistered documents cannot be used as evidence of title",
                        "relevance": "Registration requirements for property transfers",
                        "keywords": ["registration", "immovable property", "sale deed", "evidence"]
                    },
                    {
                        "case_name": "Suraj Lamp & Industries v. State of Haryana",
                        "citation": "AIR 2012 SC 438",
                        "court": "Supreme Court of India",
                        "year": 2012,
                        "legal_principle": "Stamp duty is a tax on instruments, not on transactions",
                        "facts": "Challenge to stamp duty assessment on lease deed",
                        "holding": "Proper stamp duty must be paid on instruments to make them admissible",
                        "relevance": "Stamp duty requirements and consequences",
                        "keywords": ["stamp duty", "instrument", "admissibility", "tax"]
                    }
                ],
                "corporate_law": [
                    {
                        "case_name": "Salomon v. Salomon & Co. Ltd.",
                        "citation": "AIR 1897 AC 22",
                        "court": "House of Lords",
                        "year": 1897,
                        "legal_principle": "Company has separate legal personality distinct from its members",
                        "facts": "Sole proprietor incorporated company and became secured creditor",
                        "holding": "Company is separate legal entity with its own rights and liabilities",
                        "relevance": "Corporate personality and limited liability",
                        "keywords": ["separate legal entity", "corporate veil", "limited liability"]
                    }
                ]
            },
            "usa": {
                "contract_law": [
                    {
                        "case_name": "Hadley v. Baxendale",
                        "citation": "156 Eng. Rep. 145 (1854)",
                        "court": "Court of Exchequer",
                        "year": 1854,
                        "legal_principle": "Damages for breach of contract limited to foreseeable consequences",
                        "facts": "Mill owner sued carrier for delayed delivery of mill shaft",
                        "holding": "Damages must arise naturally from breach or be reasonably foreseeable",
                        "relevance": "Measure of damages in contract breach",
                        "keywords": ["damages", "foreseeability", "breach of contract", "consequential damages"]
                    },
                    {
                        "case_name": "Lucy v. Zehmer",
                        "citation": "196 Va. 493, 84 S.E.2d 516 (1954)",
                        "court": "Supreme Court of Virginia",
                        "year": 1954,
                        "legal_principle": "Objective test applies to determine contractual intent",
                        "facts": "Land sale agreement written on restaurant napkin during drinking",
                        "holding": "Contract formation judged by objective manifestation of intent, not subjective intent",
                        "relevance": "Contract formation and intent",
                        "keywords": ["objective test", "contractual intent", "offer and acceptance"]
                    },
                    {
                        "case_name": "Hamer v. Sidway",
                        "citation": "124 N.Y. 538, 27 N.E. 256 (1891)",
                        "court": "New York Court of Appeals",
                        "year": 1891,
                        "legal_principle": "Forbearance from legal right constitutes valid consideration",
                        "facts": "Uncle promised nephew money if he refrained from drinking and smoking",
                        "holding": "Giving up legal right is sufficient consideration for contract",
                        "relevance": "Consideration requirements",
                        "keywords": ["consideration", "forbearance", "legal detriment", "bargain"]
                    }
                ],
                "corporate_law": [
                    {
                        "case_name": "Business Judgment Rule - Smith v. Van Gorkom",
                        "citation": "488 A.2d 858 (Del. 1985)",
                        "court": "Delaware Supreme Court",
                        "year": 1985,
                        "legal_principle": "Directors must make informed decisions to receive business judgment rule protection",
                        "facts": "Board approved merger without adequate investigation",
                        "holding": "Directors breached duty of care by failing to inform themselves",
                        "relevance": "Director duties and business judgment rule",
                        "keywords": ["business judgment rule", "duty of care", "informed decision", "directors"]
                    }
                ],
                "securities_law": [
                    {
                        "case_name": "SEC v. W.J. Howey Co.",
                        "citation": "328 U.S. 293 (1946)",
                        "court": "U.S. Supreme Court",
                        "year": 1946,
                        "legal_principle": "Investment contract test for determining what constitutes a security",
                        "facts": "Sale of citrus groves with management contracts",
                        "holding": "Investment contract exists when money invested in common enterprise with expectation of profits from others' efforts",
                        "relevance": "Definition of securities and investment contracts",
                        "keywords": ["Howey test", "investment contract", "security", "common enterprise"]
                    }
                ],
                "employment_law": [
                    {
                        "case_name": "McDonnell Douglas Corp. v. Green",
                        "citation": "411 U.S. 792 (1973)",
                        "court": "U.S. Supreme Court",
                        "year": 1973,
                        "legal_principle": "Framework for proving employment discrimination claims",
                        "facts": "Employee claimed racial discrimination in hiring",
                        "holding": "Established burden-shifting framework for discrimination claims",
                        "relevance": "Employment discrimination proof standards",
                        "keywords": ["employment discrimination", "burden of proof", "prima facie case", "pretext"]
                    }
                ]
            }
        }
        
        # Get case law for jurisdiction
        jurisdiction_cases = case_law_db.get(jurisdiction.lower())
        if not jurisdiction_cases:
            raise HTTPException(status_code=404, detail=f"No case law available for jurisdiction: {jurisdiction}")
        
        # Filter by legal area if specified
        if legal_area:
            area_cases = jurisdiction_cases.get(legal_area.lower())
            if not area_cases:
                available_areas = list(jurisdiction_cases.keys())
                raise HTTPException(
                    status_code=404,
                    detail=f"Legal area '{legal_area}' not found. Available areas: {available_areas}"
                )
            result_cases = {legal_area.lower(): area_cases}
        else:
            result_cases = jurisdiction_cases
        
        # Apply search filter if specified
        if search_term:
            filtered_cases = {}
            search_lower = search_term.lower()
            
            for area, cases in result_cases.items():
                filtered_area_cases = []
                for case in cases:
                    # Search in case name, legal principle, facts, holding, and keywords
                    if (search_lower in case.get("case_name", "").lower() or
                        search_lower in case.get("legal_principle", "").lower() or
                        search_lower in case.get("facts", "").lower() or
                        search_lower in case.get("holding", "").lower() or
                        any(search_lower in keyword.lower() for keyword in case.get("keywords", []))):
                        filtered_area_cases.append(case)
                
                if filtered_area_cases:
                    filtered_cases[area] = filtered_area_cases[:limit]
            
            result_cases = filtered_cases
        else:
            # Apply limit to each area
            for area in result_cases:
                result_cases[area] = result_cases[area][:limit]
        
        return {
            "jurisdiction": jurisdiction.lower(),
            "legal_area": legal_area,
            "search_term": search_term,
            "limit": limit,
            "cases": result_cases,
            "metadata": {
                "total_areas": len(result_cases),
                "total_cases": sum(len(cases) for cases in result_cases.values()),
                "available_areas": list(jurisdiction_cases.keys()) if not legal_area else None,
                "last_updated": "2024-01-01T00:00:00Z"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving case law for {jurisdiction}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve case law precedents")