"""File storage service for handling document uploads."""

import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class FileService:
    """Service for handling file storage operations."""
    
    @staticmethod
    def _ensure_upload_directory() -> Path:
        """
        Ensure the upload directory exists.
        
        Returns:
            Path: The upload directory path
        """
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir
    
    @staticmethod
    def _validate_file(file: UploadFile) -> None:
        """
        Validate uploaded file.
        
        Args:
            file: The uploaded file
            
        Raises:
            HTTPException: If file validation fails
        """
        # Check file size
        if file.size and file.size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"
            )
        
        # Check file type
        if file.content_type:
            # Extract file extension from content type or filename
            file_ext = None
            if file.filename:
                file_ext = Path(file.filename).suffix.lower().lstrip('.')
            
            allowed_types = settings.allowed_file_types_list
            
            # Check by extension
            if file_ext and file_ext not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type '{file_ext}' not allowed. Allowed types: {', '.join(allowed_types)}"
                )
            
            # Check by MIME type for common document types
            allowed_mime_types = {
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain'
            }
            
            if file.content_type not in allowed_mime_types and file_ext not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type not supported. Content type: {file.content_type}"
                )
    
    @staticmethod
    async def save_file(file: UploadFile, user_id: str) -> Tuple[str, int]:
        """
        Save uploaded file to storage.
        
        Args:
            file: The uploaded file
            user_id: ID of the user uploading the file
            
        Returns:
            Tuple[str, int]: File path and file size
            
        Raises:
            HTTPException: If file saving fails
        """
        try:
            # Validate file
            FileService._validate_file(file)
            
            # Ensure upload directory exists
            upload_dir = FileService._ensure_upload_directory()
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            original_name = file.filename or "unknown"
            file_ext = Path(original_name).suffix
            filename = f"{file_id}{file_ext}"
            
            # Create user-specific subdirectory
            user_dir = upload_dir / user_id
            user_dir.mkdir(exist_ok=True)
            
            file_path = user_dir / filename
            
            # Save file
            file_size = 0
            async with aiofiles.open(file_path, 'wb') as f:
                while chunk := await file.read(8192):  # Read in 8KB chunks
                    file_size += len(chunk)
                    await f.write(chunk)
            
            # Reset file position for potential re-reading
            await file.seek(0)
            
            logger.info(f"Saved file {original_name} as {file_path} ({file_size} bytes)")
            
            return str(file_path), file_size
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save file"
            )
    
    @staticmethod
    async def delete_file(file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            bool: True if file was deleted successfully
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    @staticmethod
    async def get_file_content(file_path: str) -> Optional[bytes]:
        """
        Read file content from storage.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bytes: File content, or None if file not found
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            async with aiofiles.open(path, 'rb') as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    @staticmethod
    def get_file_info(file_path: str) -> Optional[dict]:
        """
        Get file information.
        
        Args:
            file_path: Path to the file
            
        Returns:
            dict: File information, or None if file not found
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "exists": True
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None