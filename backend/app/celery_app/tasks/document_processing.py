"""Document processing tasks for Celery workers."""

import asyncio
import logging
from typing import Dict, Any, Optional
from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app.celery import celery_app, TaskProgress, DocumentProcessingError
from app.database.connection import AsyncSessionLocal
from app.core.document_processor import PDFExtractor, DocumentStructureAnalyzer
from app.database.models import Document, AnalysisResults
from app.schemas.document import AnalysisStatus

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="process_document")
def process_document_task(self, document_id: str) -> Dict[str, Any]:
    """
    Process a document: extract text, analyze structure, and prepare for AI analysis.
    
    Args:
        document_id: The ID of the document to process
        
    Returns:
        Dict containing processing results and metadata
    """
    task_id = self.request.id
    logger.info(f"Starting document processing for document {document_id}")
    
    try:
        # Update progress
        TaskProgress.update_progress(task_id, 0, 100, "Starting document processing")
        
        # Run async processing in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _process_document_async(document_id, task_id)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Document processing failed for {document_id}: {exc}")
        raise DocumentProcessingError(f"Failed to process document: {str(exc)}")


async def _process_document_async(document_id: str, task_id: str) -> Dict[str, Any]:
    """Async document processing implementation."""
    
    async with AsyncSessionLocal() as session:
        # Get document from database
        TaskProgress.update_progress(task_id, 10, 100, "Loading document from database")
        
        document = await session.get(Document, document_id)
        if not document:
            raise DocumentProcessingError(f"Document {document_id} not found")
        
        # Update document status
        document.analysis_status = AnalysisStatus.PROCESSING
        await session.commit()
        
        try:
            # Initialize processors
            pdf_extractor = PDFExtractor()
            structure_analyzer = DocumentStructureAnalyzer()
            
            # Extract text from document
            TaskProgress.update_progress(task_id, 30, 100, "Extracting text from document")
            
            extraction_result = pdf_extractor.extract_text(document.file_path)
            
            if extraction_result.errors:
                raise DocumentProcessingError(f"Text extraction failed: {'; '.join(extraction_result.errors)}")
            
            # Analyze document structure
            TaskProgress.update_progress(task_id, 60, 100, "Analyzing document structure")
            
            structure_result = structure_analyzer.analyze_structure(extraction_result.text)
            
            # Update document with extracted content
            TaskProgress.update_progress(task_id, 80, 100, "Updating document in database")
            
            document.content = extraction_result.text
            document.metadata = {
                **document.metadata,
                "extraction_method": extraction_result.method.value,
                "page_count": extraction_result.page_count,
                "word_count": len(extraction_result.text.split()),
                "character_count": len(extraction_result.text),
                "structure": [{"title": s.title, "level": s.level} for s in structure_result.sections],
                "document_type": structure_result.document_type.value,
            }
            document.analysis_status = AnalysisStatus.COMPLETED
            
            await session.commit()
            
            TaskProgress.update_progress(task_id, 100, 100, "Document processing completed")
            
            return {
                "document_id": document_id,
                "status": "success",
                "extraction_method": extraction_result.method.value,
                "page_count": extraction_result.page_count,
                "word_count": len(extraction_result.text.split()),
                "sections_found": len(structure_result.sections),
                "document_type": structure_result.document_type.value,
            }
            
        except Exception as exc:
            # Update document status on failure
            document.analysis_status = AnalysisStatus.FAILED
            document.error_message = str(exc)
            await session.commit()
            raise exc


@celery_app.task(bind=True, name="extract_document_text")
def extract_document_text_task(self, file_path: str, document_id: str) -> Dict[str, Any]:
    """
    Extract text from a document file.
    
    Args:
        file_path: Path to the document file
        document_id: ID of the document for progress tracking
        
    Returns:
        Dict containing extracted text and metadata
    """
    task_id = self.request.id
    logger.info(f"Starting text extraction for file {file_path}")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting text extraction")
        
        # Run async extraction
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _extract_text_async(file_path, task_id)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Text extraction failed for {file_path}: {exc}")
        raise DocumentProcessingError(f"Failed to extract text: {str(exc)}")


async def _extract_text_async(file_path: str, task_id: str) -> Dict[str, Any]:
    """Async text extraction implementation."""
    
    TaskProgress.update_progress(task_id, 20, 100, "Initializing PDF extractor")
    
    pdf_extractor = PDFExtractor()
    
    TaskProgress.update_progress(task_id, 40, 100, "Extracting text from PDF")
    
    result = pdf_extractor.extract_text(file_path)
    
    if result.errors:
        raise DocumentProcessingError(f"Text extraction failed: {'; '.join(result.errors)}")
    
    TaskProgress.update_progress(task_id, 100, 100, "Text extraction completed")
    
    return {
        "text": result.text,
        "metadata": {"page_count": result.page_count, "confidence": result.confidence},
        "extraction_method": result.method.value,
        "success": True,
    }


@celery_app.task(bind=True, name="analyze_document_structure")
def analyze_document_structure_task(
    self, 
    text: str, 
    metadata: Dict[str, Any],
    document_id: str
) -> Dict[str, Any]:
    """
    Analyze document structure and identify sections.
    
    Args:
        text: Document text content
        metadata: Document metadata
        document_id: ID of the document for progress tracking
        
    Returns:
        Dict containing structure analysis results
    """
    task_id = self.request.id
    logger.info(f"Starting structure analysis for document {document_id}")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting structure analysis")
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _analyze_structure_async(text, metadata, task_id)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Structure analysis failed for document {document_id}: {exc}")
        raise DocumentProcessingError(f"Failed to analyze structure: {str(exc)}")


async def _analyze_structure_async(
    text: str, 
    metadata: Dict[str, Any], 
    task_id: str
) -> Dict[str, Any]:
    """Async structure analysis implementation."""
    
    TaskProgress.update_progress(task_id, 20, 100, "Initializing structure analyzer")
    
    structure_analyzer = DocumentStructureAnalyzer()
    
    TaskProgress.update_progress(task_id, 50, 100, "Analyzing document structure")
    
    result = structure_analyzer.analyze_structure(text)
    
    TaskProgress.update_progress(task_id, 100, 100, "Structure analysis completed")
    
    return {
        "sections": [{"title": s.title, "level": s.level, "content": s.content} for s in result.sections],
        "document_type": result.document_type.value,
        "parties": result.parties,
        "dates": result.dates,
        "key_terms": result.key_terms,
        "metadata": result.metadata,
        "success": True,
    }


@celery_app.task(bind=True, name="batch_process_documents")
def batch_process_documents_task(self, document_ids: list[str]) -> Dict[str, Any]:
    """
    Process multiple documents in batch.
    
    Args:
        document_ids: List of document IDs to process
        
    Returns:
        Dict containing batch processing results
    """
    task_id = self.request.id
    logger.info(f"Starting batch processing for {len(document_ids)} documents")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting batch processing")
        
        results = []
        total_docs = len(document_ids)
        
        for i, doc_id in enumerate(document_ids):
            try:
                # Process individual document
                progress = int((i / total_docs) * 90)  # Reserve 10% for final steps
                TaskProgress.update_progress(
                    task_id, 
                    progress, 
                    100, 
                    f"Processing document {i+1}/{total_docs}"
                )
                
                # Trigger individual document processing
                result = process_document_task.delay(doc_id)
                results.append({
                    "document_id": doc_id,
                    "task_id": result.id,
                    "status": "queued"
                })
                
            except Exception as exc:
                logger.error(f"Failed to queue document {doc_id}: {exc}")
                results.append({
                    "document_id": doc_id,
                    "status": "failed",
                    "error": str(exc)
                })
        
        TaskProgress.update_progress(task_id, 100, 100, "Batch processing completed")
        
        return {
            "total_documents": total_docs,
            "queued_successfully": len([r for r in results if r["status"] == "queued"]),
            "failed_to_queue": len([r for r in results if r["status"] == "failed"]),
            "results": results,
        }
        
    except Exception as exc:
        logger.error(f"Batch processing failed: {exc}")
        raise DocumentProcessingError(f"Failed to process batch: {str(exc)}")