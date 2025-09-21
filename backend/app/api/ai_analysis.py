"""AI Analysis API endpoints."""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json

from app.core.dependencies import get_current_user
from app.services.ai_analysis_service import AIAnalysisService
from app.schemas.base import BaseResponse
from app.core.exceptions import AIProcessingError, InvalidInputError


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Analysis"])

# Initialize AI service (in production, use dependency injection)
ai_service = AIAnalysisService()


# Request/Response Models
class DocumentAnalysisRequest(BaseModel):
    """Request model for document analysis."""
    document_content: str = Field(..., description="Document text content")
    document_type: str = Field(..., description="Type of document (contract, agreement, etc.)")
    jurisdiction_hint: Optional[str] = Field(None, description="Optional jurisdiction hint")
    analysis_options: Optional[Dict[str, Any]] = Field(None, description="Additional analysis options")


class QuickAnalysisRequest(BaseModel):
    """Request model for quick analysis."""
    document_content: str = Field(..., description="Document text content")
    document_type: str = Field(..., description="Type of document")
    analysis_type: str = Field("executive_summary", description="Type of analysis to perform")
    jurisdiction_hint: Optional[str] = Field(None, description="Optional jurisdiction hint")


class ChatRequest(BaseModel):
    """Request model for chat interaction."""
    session_id: str = Field(..., description="Conversation session ID")
    question: str = Field(..., description="User's question about the document")
    document_content: Optional[str] = Field(None, description="Document text (if not in session)")
    document_id: Optional[str] = Field(None, description="Document identifier")
    jurisdiction: Optional[str] = Field(None, description="Legal jurisdiction context")


class StreamChatRequest(BaseModel):
    """Request model for streaming chat."""
    session_id: str = Field(..., description="Conversation session ID")
    question: str = Field(..., description="User's question")
    document_content: Optional[str] = Field(None, description="Document text")
    jurisdiction: Optional[str] = Field(None, description="Legal jurisdiction context")


class JurisdictionAnalysisRequest(BaseModel):
    """Request model for jurisdiction-specific analysis."""
    document_content: str = Field(..., description="Document text")
    document_type: str = Field(..., description="Type of document")
    jurisdiction: str = Field(..., description="Legal jurisdiction")
    analysis_type: str = Field(..., description="Specific analysis type")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")


class DocumentComparisonRequest(BaseModel):
    """Request model for document comparison."""
    document1_content: str = Field(..., description="First document text")
    document2_content: str = Field(..., description="Second document text")
    document1_type: str = Field(..., description="Type of first document")
    document2_type: str = Field(..., description="Type of second document")
    comparison_type: str = Field("comprehensive", description="Type of comparison")


class AnalysisResponse(BaseResponse):
    """Response model for analysis results."""
    analysis_id: Optional[str] = None
    results: Dict[str, Any]
    processing_time_seconds: Optional[float] = None


class ChatResponse(BaseResponse):
    """Response model for chat interaction."""
    response: str
    session_id: str
    metadata: Dict[str, Any]


# API Endpoints

@router.post("/analyze/comprehensive", response_model=AnalysisResponse)
async def analyze_document_comprehensive(
    request: DocumentAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
) -> AnalysisResponse:
    """
    Perform comprehensive document analysis with jurisdiction awareness.
    
    This endpoint provides full document analysis including:
    - Jurisdiction detection
    - Executive summary
    - Risk analysis
    - Obligation extraction
    - Complexity scoring
    - Jurisdiction-specific analysis
    """
    try:
        logger.info(f"Starting comprehensive analysis for user {current_user.id}")
        
        # Generate unique document ID for this analysis
        import uuid
        document_id = str(uuid.uuid4())
        
        # Perform comprehensive analysis
        results = await ai_service.analyze_document_comprehensive(
            document_id=document_id,
            document_content=request.document_content,
            document_type=request.document_type,
            user_id=str(current_user.id),
            jurisdiction_hint=request.jurisdiction_hint,
            analysis_options=request.analysis_options
        )
        
        return AnalysisResponse(
            success=True,
            message="Comprehensive analysis completed successfully",
            analysis_id=document_id,
            results=results,
            processing_time_seconds=results.get("metadata", {}).get("processing_time_seconds")
        )
        
    except AIProcessingError as e:
        logger.error(f"AI processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in comprehensive analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis"
        )


@router.post("/analyze/quick", response_model=AnalysisResponse)
async def analyze_document_quick(
    request: QuickAnalysisRequest,
    current_user = Depends(get_current_user)
) -> AnalysisResponse:
    """
    Perform quick document analysis for specific analysis type.
    
    Available analysis types:
    - executive_summary
    - risk_analysis
    - obligation_extraction
    - complexity_scoring
    - jurisdiction_analysis
    - compliance_check
    """
    try:
        logger.info(f"Starting quick analysis ({request.analysis_type}) for user {current_user.id}")
        
        results = await ai_service.analyze_document_quick(
            document_content=request.document_content,
            document_type=request.document_type,
            analysis_type=request.analysis_type,
            jurisdiction_hint=request.jurisdiction_hint
        )
        
        return AnalysisResponse(
            success=True,
            message=f"Quick {request.analysis_type} analysis completed successfully",
            results=results
        )
        
    except AIProcessingError as e:
        logger.error(f"AI processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in quick analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_document(
    request: ChatRequest,
    current_user = Depends(get_current_user)
) -> ChatResponse:
    """
    Interactive chat about a document with AI assistance.
    
    Provides contextual Q&A about legal documents with:
    - Document-specific context
    - Jurisdiction awareness
    - Conversation memory
    - Legal citations and references
    """
    try:
        logger.info(f"Processing chat request for user {current_user.id}, session {request.session_id}")
        
        response = await ai_service.chat_with_document(
            session_id=request.session_id,
            question=request.question,
            document_content=request.document_content,
            document_id=request.document_id,
            user_id=str(current_user.id),
            jurisdiction=request.jurisdiction
        )
        
        return ChatResponse(
            success=True,
            message="Chat response generated successfully",
            response=response["response"],
            session_id=request.session_id,
            metadata=response["metadata"]
        )
        
    except AIProcessingError as e:
        logger.error(f"AI processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during chat processing"
        )


@router.post("/chat/stream")
async def stream_chat_response(
    request: StreamChatRequest,
    current_user = Depends(get_current_user)
):
    """
    Stream chat response for real-time interaction.
    
    Provides streaming responses for better user experience during
    longer AI processing times.
    """
    try:
        logger.info(f"Starting streaming chat for user {current_user.id}, session {request.session_id}")
        
        async def generate_stream():
            try:
                async for chunk in ai_service.stream_chat_response(
                    session_id=request.session_id,
                    question=request.question,
                    document_content=request.document_content,
                    user_id=str(current_user.id),
                    jurisdiction=request.jurisdiction
                ):
                    # Format as Server-Sent Events
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                logger.error(f"Error in streaming chat: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in streaming chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during streaming chat"
        )


@router.post("/analyze/jurisdiction-specific", response_model=AnalysisResponse)
async def analyze_jurisdiction_specific(
    request: JurisdictionAnalysisRequest,
    current_user = Depends(get_current_user)
) -> AnalysisResponse:
    """
    Perform jurisdiction-specific analysis.
    
    Available analyses by jurisdiction:
    
    India:
    - stamp_duty_calculation
    - gst_analysis
    - contract_act_compliance
    - companies_act_compliance
    
    USA:
    - ucc_analysis
    - securities_compliance
    - privacy_compliance
    - state_law_analysis
    
    Cross-border:
    - enforceability_comparison
    - tax_implications
    - formalities_comparison
    """
    try:
        logger.info(f"Starting jurisdiction-specific analysis ({request.analysis_type}) for user {current_user.id}")
        
        results = await ai_service.analyze_jurisdiction_specific(
            document_content=request.document_content,
            document_type=request.document_type,
            jurisdiction=request.jurisdiction,
            analysis_type=request.analysis_type,
            **(request.parameters or {})
        )
        
        return AnalysisResponse(
            success=True,
            message=f"Jurisdiction-specific {request.analysis_type} analysis completed successfully",
            results=results
        )
        
    except AIProcessingError as e:
        logger.error(f"AI processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Jurisdiction-specific analysis failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in jurisdiction-specific analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis"
        )


@router.post("/compare", response_model=AnalysisResponse)
async def compare_documents(
    request: DocumentComparisonRequest,
    current_user = Depends(get_current_user)
) -> AnalysisResponse:
    """
    Compare two documents with AI analysis.
    
    Provides comprehensive document comparison including:
    - Jurisdiction-aware comparison
    - Cross-border analysis (if applicable)
    - Clause-by-clause differences
    - Risk comparison
    - Compliance differences
    """
    try:
        logger.info(f"Starting document comparison for user {current_user.id}")
        
        results = await ai_service.compare_documents(
            document1_content=request.document1_content,
            document2_content=request.document2_content,
            document1_type=request.document1_type,
            document2_type=request.document2_type,
            comparison_type=request.comparison_type
        )
        
        return AnalysisResponse(
            success=True,
            message="Document comparison completed successfully",
            results=results
        )
        
    except AIProcessingError as e:
        logger.error(f"AI processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document comparison failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in document comparison: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during comparison"
        )


# Information endpoints

@router.get("/analysis-types")
async def get_supported_analysis_types(
    current_user = Depends(get_current_user)
) -> Dict[str, List[str]]:
    """Get list of supported analysis types."""
    return {
        "general_analysis_types": ai_service.get_supported_analysis_types(),
        "supported_jurisdictions": ai_service.get_supported_jurisdictions()
    }


@router.get("/jurisdiction/{jurisdiction}/analysis-types")
async def get_jurisdiction_analysis_types(
    jurisdiction: str,
    current_user = Depends(get_current_user)
) -> Dict[str, List[str]]:
    """Get jurisdiction-specific analysis types."""
    try:
        analysis_types = ai_service.get_jurisdiction_specific_analyses(jurisdiction)
        return {
            "jurisdiction": jurisdiction,
            "analysis_types": analysis_types
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid jurisdiction: {jurisdiction}"
        )


@router.get("/analysis/{analysis_id}/status")
async def get_analysis_status(
    analysis_id: str,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get the status of a running analysis."""
    try:
        status_info = await ai_service.get_analysis_status(analysis_id)
        return status_info
    except Exception as e:
        logger.error(f"Error getting analysis status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis not found: {analysis_id}"
        )