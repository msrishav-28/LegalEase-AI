"""Document service for document management operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status, UploadFile
from typing import Optional, List, Tuple
import logging
import uuid
from pathlib import Path

from app.database.models.document import Document, DocumentType, AnalysisStatus
from app.database.models.user import User
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentListResponse
from app.services.file_service import FileService

logger = logging.getLogger(__name__)


class DocumentService:
    """Service class for document management operations."""
    
    @staticmethod
    async def upload_document(
        db: AsyncSession, 
        file: UploadFile, 
        user: User,
        document_name: Optional[str] = None,
        document_type: DocumentType = DocumentType.OTHER
    ) -> Document:
        """
        Upload and create a new document.
        
        Args:
            db: Database session
            file: Uploaded file
            user: User uploading the document
            document_name: Optional custom name for the document
            document_type: Type of document
            
        Returns:
            Document: The created document
            
        Raises:
            HTTPException: If upload fails
        """
        try:
            # Save file to storage
            file_path, file_size = await FileService.save_file(file, str(user.id))
            
            # Use provided name or filename
            name = document_name or file.filename or "Untitled Document"
            
            # Create document record
            document_data = DocumentCreate(
                name=name,
                original_filename=file.filename or "unknown",
                file_path=file_path,
                file_size=file_size,
                mime_type=file.content_type or "application/octet-stream",
                document_type=document_type
            )
            
            document = Document(
                name=document_data.name,
                original_filename=document_data.original_filename,
                file_path=document_data.file_path,
                file_size=document_data.file_size,
                mime_type=document_data.mime_type,
                document_type=document_data.document_type,
                analysis_status=AnalysisStatus.PENDING,
                uploaded_by=user.id
            )
            
            db.add(document)
            await db.commit()
            await db.refresh(document)
            
            logger.info(f"Document uploaded: {document.name} by user {user.email}")
            return document
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            # Clean up file if document creation failed
            if 'file_path' in locals():
                await FileService.delete_file(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document upload failed"
            )
    
    @staticmethod
    async def get_document_by_id(
        db: AsyncSession, 
        document_id: str, 
        user: User
    ) -> Optional[Document]:
        """
        Get a document by ID.
        
        Args:
            db: Database session
            document_id: Document ID
            user: User requesting the document
            
        Returns:
            Document: The document, or None if not found
        """
        try:
            # Convert string to UUID if needed
            if isinstance(document_id, str):
                document_id = uuid.UUID(document_id)
            
            result = await db.execute(
                select(Document).where(
                    Document.id == document_id,
                    Document.uploaded_by == user.id
                )
            )
            return result.scalar_one_or_none()
        except ValueError:
            return None
    
    @staticmethod
    async def get_user_documents(
        db: AsyncSession,
        user: User,
        page: int = 1,
        size: int = 20,
        document_type: Optional[DocumentType] = None
    ) -> DocumentListResponse:
        """
        Get documents for a user with pagination.
        
        Args:
            db: Database session
            user: User requesting documents
            page: Page number (1-based)
            size: Page size
            document_type: Optional filter by document type
            
        Returns:
            DocumentListResponse: Paginated document list
        """
        try:
            # Build query
            query = select(Document).where(Document.uploaded_by == user.id)
            
            if document_type:
                query = query.where(Document.document_type == document_type)
            
            # Get total count
            count_query = select(func.count(Document.id)).where(Document.uploaded_by == user.id)
            if document_type:
                count_query = count_query.where(Document.document_type == document_type)
            
            total_result = await db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            offset = (page - 1) * size
            query = query.offset(offset).limit(size).order_by(Document.created_at.desc())
            
            result = await db.execute(query)
            documents = result.scalars().all()
            
            # Calculate pagination info
            pages = (total + size - 1) // size  # Ceiling division
            
            return DocumentListResponse(
                documents=documents,
                total=total,
                page=page,
                size=size,
                pages=pages
            )
            
        except Exception as e:
            logger.error(f"Error getting user documents: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve documents"
            )
    
    @staticmethod
    async def update_document(
        db: AsyncSession,
        document: Document,
        update_data: DocumentUpdate
    ) -> Document:
        """
        Update a document.
        
        Args:
            db: Database session
            document: Document to update
            update_data: Update data
            
        Returns:
            Document: Updated document
        """
        try:
            update_dict = update_data.model_dump(exclude_unset=True)
            
            for field, value in update_dict.items():
                setattr(document, field, value)
            
            await db.commit()
            await db.refresh(document)
            
            logger.info(f"Document updated: {document.name}")
            return document
            
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document update failed"
            )
    
    @staticmethod
    async def delete_document(
        db: AsyncSession,
        document: Document
    ) -> bool:
        """
        Delete a document and its associated file.
        
        Args:
            db: Database session
            document: Document to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Delete file from storage
            await FileService.delete_file(document.file_path)
            
            # Delete document record
            await db.delete(document)
            await db.commit()
            
            logger.info(f"Document deleted: {document.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document deletion failed"
            )
    
    @staticmethod
    async def get_document_content(document: Document) -> Optional[bytes]:
        """
        Get document file content.
        
        Args:
            document: Document to get content for
            
        Returns:
            bytes: File content, or None if not found
        """
        return await FileService.get_file_content(document.file_path)