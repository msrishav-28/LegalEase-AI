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
from app.schemas.security import SecureDocumentUpload, SecureDocumentUpdate
from app.database.models.document import DocumentType
from app.database.models.user import User
from app.services.document_service import DocumentService
from app.core.dependencies import get_current_active_user
from app.core.security import FileValidator, InputValidator

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
    Upload a new document with comprehensive security validation.
    
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
        # Validate file is provided
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Read file content for validation
        file_content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Validate filename
        try:
            validated_filename = InputValidator.validate_filename(file.filename)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid filename: {str(e)}"
            )
        
        # Validate document name if provided
        if name:
            try:
                name = InputValidator.validate_string(name, max_length=255)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid document name: {str(e)}"
                )
        
        # Comprehensive file validation
        validation_result = await FileValidator.validate_file_upload(
            file_content=file_content,
            filename=validated_filename,
            mime_type=file.content_type or "application/octet-stream"
        )
        
        if not validation_result['valid']:
            logger.warning(f"File validation failed for user {current_user.id}: {validation_result['errors']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File validation failed: {'; '.join(validation_result['errors'])}"
            )
        
        # Log warnings if any
        if validation_result['warnings']:
            logger.warning(f"File validation warnings for user {current_user.id}: {validation_result['warnings']}")
        
        # Create secure upload data
        upload_data = SecureDocumentUpload(
            name=name,
            document_type=document_type.value
        )
        
        document = await DocumentService.upload_document(
            db=db,
            file=file,
            user=current_user,
            document_name=upload_data.name,
            document_type=document_type
        )
        
        logger.info(f"Document uploaded successfully by user {current_user.id}: {document.id}")
        
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
    update_data: SecureDocumentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a document with security validation.
    
    Args:
        document_id: Document ID
        update_data: Update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        DocumentResponse: Updated document information
    """
    try:
        # Validate document ID
        try:
            validated_doc_id = InputValidator.validate_document_id(document_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document ID: {str(e)}"
            )
        
        document = await DocumentService.get_document_by_id(
            db=db,
            document_id=validated_doc_id,
            user=current_user
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Convert secure schema to regular update schema
        regular_update_data = DocumentUpdate(
            name=update_data.name,
            document_type=update_data.document_type,
            metadata=update_data.metadata
        )
        
        updated_document = await DocumentService.update_document(
            db=db,
            document=document,
            update_data=regular_update_data
        )
        
        logger.info(f"Document updated successfully by user {current_user.id}: {document.id}")
        
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