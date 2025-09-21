"""Semantic search API endpoints."""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.core.dependencies import get_current_user
from app.services.semantic_search_service import SemanticSearchService
from app.schemas.base import BaseResponse
from app.core.exceptions import AIProcessingError, InvalidInputError


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Semantic Search"])

# Initialize semantic search service
search_service = SemanticSearchService()


# Request/Response Models
class DocumentIndexRequest(BaseModel):
    """Request model for adding document to search index."""
    document_id: str = Field(..., description="Unique document identifier")
    document_content: str = Field(..., description="Document text content")
    document_type: str = Field(..., description="Type of document")
    jurisdiction: Optional[str] = Field(None, description="Legal jurisdiction")
    additional_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SearchRequest(BaseModel):
    """Request model for document search."""
    query: str = Field(..., description="Search query text")
    document_type: Optional[str] = Field(None, description="Filter by document type")
    jurisdiction: Optional[str] = Field(None, description="Filter by jurisdiction")
    top_k: int = Field(10, description="Maximum number of results", ge=1, le=50)
    min_score: float = Field(0.7, description="Minimum similarity score", ge=0.0, le=1.0)


class ClauseSearchRequest(BaseModel):
    """Request model for similar clause search."""
    clause_text: str = Field(..., description="Clause text to find similarities for")
    document_type: Optional[str] = Field(None, description="Filter by document type")
    jurisdiction: Optional[str] = Field(None, description="Filter by jurisdiction")
    top_k: int = Field(5, description="Number of similar clauses to return", ge=1, le=20)
    include_analysis: bool = Field(True, description="Include AI analysis of similarities")


class LegalConceptSearchRequest(BaseModel):
    """Request model for legal concept search."""
    legal_concept: str = Field(..., description="Legal concept to search for")
    jurisdiction: Optional[str] = Field(None, description="Filter by jurisdiction")
    document_type: Optional[str] = Field(None, description="Filter by document type")
    top_k: int = Field(10, description="Number of results to return", ge=1, le=30)


class PrecedentSearchRequest(BaseModel):
    """Request model for precedent document search."""
    document_content: str = Field(..., description="Document content to find precedents for")
    document_type: str = Field(..., description="Type of document")
    jurisdiction: Optional[str] = Field(None, description="Legal jurisdiction")
    top_k: int = Field(5, description="Number of precedents to return", ge=1, le=10)


class SectionSearchRequest(BaseModel):
    """Request model for section-based search."""
    section_type: str = Field(..., description="Type of section to search in")
    query: Optional[str] = Field(None, description="Optional query text for semantic search")
    document_type: Optional[str] = Field(None, description="Filter by document type")
    jurisdiction: Optional[str] = Field(None, description="Filter by jurisdiction")
    top_k: int = Field(10, description="Number of results to return", ge=1, le=30)


class SearchResponse(BaseResponse):
    """Response model for search results."""
    results: List[Dict[str, Any]]
    total_results: int
    query_info: Dict[str, Any]


class IndexResponse(BaseResponse):
    """Response model for indexing operations."""
    document_id: str
    processing_info: Dict[str, Any]


# API Endpoints

@router.post("/index/document", response_model=IndexResponse)
async def add_document_to_index(
    request: DocumentIndexRequest,
    current_user = Depends(get_current_user)
) -> IndexResponse:
    """
    Add a document to the semantic search index.
    
    This endpoint processes the document content, generates embeddings,
    and stores them in the vector database for semantic search.
    """
    try:
        logger.info(f"Adding document {request.document_id} to search index for user {current_user.id}")
        
        result = await search_service.add_document_to_search_index(
            document_id=request.document_id,
            document_content=request.document_content,
            document_type=request.document_type,
            jurisdiction=request.jurisdiction,
            additional_metadata=request.additional_metadata
        )
        
        return IndexResponse(
            success=True,
            message="Document successfully added to search index",
            document_id=request.document_id,
            processing_info=result
        )
        
    except AIProcessingError as e:
        logger.error(f"AI processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index document: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in document indexing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during document indexing"
        )


@router.post("/documents", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user = Depends(get_current_user)
) -> SearchResponse:
    """
    Search documents using semantic similarity.
    
    Performs vector-based semantic search across indexed documents
    with optional filtering by document type and jurisdiction.
    """
    try:
        logger.info(f"Searching documents for user {current_user.id}: '{request.query[:50]}...'")
        
        results = await search_service.search_documents(
            query=request.query,
            document_type=request.document_type,
            jurisdiction=request.jurisdiction,
            top_k=request.top_k,
            min_score=request.min_score
        )
        
        return SearchResponse(
            success=True,
            message=f"Found {len(results)} relevant documents",
            results=results,
            total_results=len(results),
            query_info={
                "query": request.query,
                "filters": {
                    "document_type": request.document_type,
                    "jurisdiction": request.jurisdiction
                },
                "parameters": {
                    "top_k": request.top_k,
                    "min_score": request.min_score
                }
            }
        )
        
    except AIProcessingError as e:
        logger.error(f"AI processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in document search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during search"
        )


@router.post("/clauses/similar", response_model=SearchResponse)
async def find_similar_clauses(
    request: ClauseSearchRequest,
    current_user = Depends(get_current_user)
) -> SearchResponse:
    """
    Find clauses similar to the provided clause text.
    
    Uses semantic similarity to find clauses with similar meaning
    and legal implications across the document corpus.
    """
    try:
        logger.info(f"Finding similar clauses for user {current_user.id}")
        
        results = await search_service.find_similar_clauses(
            clause_text=request.clause_text,
            document_type=request.document_type,
            jurisdiction=request.jurisdiction,
            top_k=request.top_k,
            include_analysis=request.include_analysis
        )
        
        return SearchResponse(
            success=True,
            message=f"Found {len(results)} similar clauses",
            results=results,
            total_results=len(results),
            query_info={
                "clause_text": request.clause_text[:100] + "..." if len(request.clause_text) > 100 else request.clause_text,
                "filters": {
                    "document_type": request.document_type,
                    "jurisdiction": request.jurisdiction
                },
                "include_analysis": request.include_analysis
            }
        )
        
    except AIProcessingError as e:
        logger.error(f"AI processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Similar clause search failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in clause search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during clause search"
        )


@router.post("/concepts/legal", response_model=SearchResponse)
async def search_legal_concepts(
    request: LegalConceptSearchRequest,
    current_user = Depends(get_current_user)
) -> SearchResponse:
    """
    Search for documents containing specific legal concepts.
    
    Finds documents that discuss or implement specific legal concepts
    like "force majeure", "indemnification", "governing law", etc.
    """
    try:
        logger.info(f"Searching legal concept '{request.legal_concept}' for user {current_user.id}")
        
        results = await search_service.search_by_legal_concept(
            legal_concept=request.legal_concept,
            jurisdiction=request.jurisdiction,
            document_type=request.document_type,
            top_k=request.top_k
        )
        
        return SearchResponse(
            success=True,
            message=f"Found {len(results)} documents containing '{request.legal_concept}'",
            results=results,
            total_results=len(results),
            query_info={
                "legal_concept": request.legal_concept,
                "filters": {
                    "jurisdiction": request.jurisdiction,
                    "document_type": request.document_type
                }
            }
        )
        
    except AIProcessingError as e:
        logger.error(f"AI processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Legal concept search failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in legal concept search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during legal concept search"
        )


@router.post("/precedents", response_model=SearchResponse)
async def find_document_precedents(
    request: PrecedentSearchRequest,
    current_user = Depends(get_current_user)
) -> SearchResponse:
    """
    Find precedent documents similar to the provided document.
    
    Identifies documents that can serve as precedents or templates
    for the provided document based on content similarity and structure.
    """
    try:
        logger.info(f"Finding precedents for {request.document_type} document for user {current_user.id}")
        
        results = await search_service.find_document_precedents(
            document_content=request.document_content,
            document_type=request.document_type,
            jurisdiction=request.jurisdiction,
            top_k=request.top_k
        )
        
        return SearchResponse(
            success=True,
            message=f"Found {len(results)} precedent documents",
            results=results,
            total_results=len(results),
            query_info={
                "document_type": request.document_type,
                "jurisdiction": request.jurisdiction,
                "content_length": len(request.document_content)
            }
        )
        
    except AIProcessingError as e:
        logger.error(f"AI processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Precedent search failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in precedent search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during precedent search"
        )


@router.post("/sections", response_model=SearchResponse)
async def search_document_sections(
    request: SectionSearchRequest,
    current_user = Depends(get_current_user)
) -> SearchResponse:
    """
    Search within specific document sections.
    
    Searches for content within specific types of document sections
    like definitions, obligations, termination clauses, etc.
    """
    try:
        logger.info(f"Searching {request.section_type} sections for user {current_user.id}")
        
        results = await search_service.search_by_document_section(
            section_type=request.section_type,
            query=request.query,
            document_type=request.document_type,
            jurisdiction=request.jurisdiction,
            top_k=request.top_k
        )
        
        return SearchResponse(
            success=True,
            message=f"Found {len(results)} results in {request.section_type} sections",
            results=results,
            total_results=len(results),
            query_info={
                "section_type": request.section_type,
                "query": request.query,
                "filters": {
                    "document_type": request.document_type,
                    "jurisdiction": request.jurisdiction
                }
            }
        )
        
    except AIProcessingError as e:
        logger.error(f"AI processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Section search failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in section search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during section search"
        )


@router.delete("/index/document/{document_id}")
async def remove_document_from_index(
    document_id: str,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Remove a document from the search index.
    
    Deletes all embeddings and metadata for the specified document
    from the vector database.
    """
    try:
        logger.info(f"Removing document {document_id} from index for user {current_user.id}")
        
        success = await search_service.remove_document_from_index(document_id)
        
        if success:
            return {
                "success": True,
                "message": f"Document {document_id} successfully removed from search index",
                "document_id": document_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found in search index"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error removing document from index: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while removing document from index"
        )


@router.get("/index/stats")
async def get_search_index_statistics(
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get statistics about the search index.
    
    Returns information about the vector database including
    total documents, index size, and performance metrics.
    """
    try:
        logger.info(f"Getting search index stats for user {current_user.id}")
        
        stats = await search_service.get_search_index_stats()
        
        return {
            "success": True,
            "message": "Search index statistics retrieved successfully",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting search index stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve search index statistics"
        )


# Information endpoints

@router.get("/section-types")
async def get_supported_section_types(
    current_user = Depends(get_current_user)
) -> Dict[str, List[str]]:
    """Get list of supported document section types for search."""
    return {
        "section_types": [
            "definitions",
            "recitals", 
            "obligations",
            "payment",
            "term",
            "termination",
            "dispute_resolution",
            "governing_law",
            "execution",
            "general"
        ],
        "description": "Document section types available for targeted search"
    }


@router.get("/legal-concepts")
async def get_common_legal_concepts(
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction"),
    current_user = Depends(get_current_user)
) -> Dict[str, List[str]]:
    """Get list of common legal concepts for search."""
    
    common_concepts = [
        "force majeure",
        "indemnification", 
        "governing law",
        "dispute resolution",
        "confidentiality",
        "intellectual property",
        "termination",
        "breach of contract",
        "limitation of liability",
        "warranties and representations"
    ]
    
    jurisdiction_specific = {
        "india": [
            "stamp duty",
            "GST implications",
            "Indian Contract Act",
            "Companies Act compliance",
            "FEMA regulations"
        ],
        "usa": [
            "UCC compliance",
            "securities regulations",
            "CCPA compliance",
            "choice of law",
            "arbitration clauses"
        ]
    }
    
    result = {
        "common_concepts": common_concepts,
        "jurisdiction_specific": {}
    }
    
    if jurisdiction and jurisdiction.lower() in jurisdiction_specific:
        result["jurisdiction_specific"][jurisdiction.lower()] = jurisdiction_specific[jurisdiction.lower()]
    else:
        result["jurisdiction_specific"] = jurisdiction_specific
    
    return result