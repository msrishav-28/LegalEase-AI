"""Document management API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging
import io

from app.database import get_db
from app.schemas.document import (
    DocumentResponse, DocumentListResponse, DocumentUploadResponse,
    DocumentUpdate
)
from app.database.models.document import DocumentType
from app.database.models.user import User
from app.services.document_service import DocumentService
from app.core.dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    document_type: DocumentType = Form(DocumentType.OTHER),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a new document.
    
    Args:
        file: The file to upload
        name: Optional custom name for the document
        document_type: Type of document
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        DocumentUploadResponse: Upload result with document info
    """
    try:
        document = await DocumentService.upload_document(
            db=db,
            file=file,
            user=current_user,
            document_name=name,
            document_type=document_type
        )
        
        return DocumentUploadResponse(
            message="Document uploaded successfully",
            document=DocumentResponse.model_validate(document)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document upload failed"
        )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    document_type: Optional[DocumentType] = Query(None, description="Filter by document type"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's documents with pagination.
    
    Args:
        page: Page number (1-based)
        size: Page size (max 100)
        document_type: Optional filter by document type
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        DocumentListResponse: Paginated list of documents
    """
    try:
        return await DocumentService.get_user_documents(
            db=db,
            user=current_user,
            page=page,
            size=size,
            document_type=document_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific document by ID.
    
    Args:
        document_id: Document ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        DocumentResponse: Document information
    """
    try:
        document = await DocumentService.get_document_by_id(
            db=db,
            document_id=document_id,
            user=current_user
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return DocumentResponse.model_validate(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document"
        )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a document.
    
    Args:
        document_id: Document ID
        update_data: Update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        DocumentResponse: Updated document information
    """
    try:
        document = await DocumentService.get_document_by_id(
            db=db,
            document_id=document_id,
            user=current_user
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        updated_document = await DocumentService.update_document(
            db=db,
            document=document,
            update_data=update_data
        )
        
        return DocumentResponse.model_validate(updated_document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document update failed"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a document.
    
    Args:
        document_id: Document ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Success message
    """
    try:
        document = await DocumentService.get_document_by_id(
            db=db,
            document_id=document_id,
            user=current_user
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        await DocumentService.delete_document(db=db, document=document)
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document deletion failed"
        )


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download a document file.
    
    Args:
        document_id: Document ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        StreamingResponse: File download response
    """
    try:
        document = await DocumentService.get_document_by_id(
            db=db,
            document_id=document_id,
            user=current_user
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get file content
        content = await DocumentService.get_document_content(document)
        
        if content is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document file not found"
            )
        
        # Create streaming response
        return StreamingResponse(
            io.BytesIO(content),
            media_type=document.mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={document.original_filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document download failed"
        )