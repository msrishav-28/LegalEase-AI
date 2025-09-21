"""AI analysis tasks for Celery workers."""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app.celery import celery_app, TaskProgress, AIAnalysisError
from app.database.connection import AsyncSessionLocal
from app.core.ai.llm_orchestrator import LLMOrchestrator
from app.core.ai.analysis_workflows import DocumentAnalysisWorkflow
from app.core.ai.vector_store import VectorStoreManager
from app.database.models import Document, AnalysisResults
from app.schemas.analysis import AnalysisStatus

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="analyze_document_with_ai")
def analyze_document_with_ai_task(self, document_id: str) -> Dict[str, Any]:
    """
    Perform comprehensive AI analysis on a document.
    
    Args:
        document_id: The ID of the document to analyze
        
    Returns:
        Dict containing AI analysis results
    """
    task_id = self.request.id
    logger.info(f"Starting AI analysis for document {document_id}")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting AI analysis")
        
        # Run async analysis in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _analyze_document_ai_async(document_id, task_id)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"AI analysis failed for document {document_id}: {exc}")
        raise AIAnalysisError(f"Failed to analyze document: {str(exc)}")


async def _analyze_document_ai_async(document_id: str, task_id: str) -> Dict[str, Any]:
    """Async AI analysis implementation."""
    
    async with AsyncSessionLocal() as session:
        # Get document from database
        TaskProgress.update_progress(task_id, 5, 100, "Loading document from database")
        
        document = await session.get(Document, document_id)
        if not document:
            raise AIAnalysisError(f"Document {document_id} not found")
        
        if not document.content:
            raise AIAnalysisError(f"Document {document_id} has no content to analyze")
        
        # Initialize AI components
        TaskProgress.update_progress(task_id, 10, 100, "Initializing AI engine")
        llm_orchestrator = LLMOrchestrator()
        analysis_workflows = DocumentAnalysisWorkflow(llm_orchestrator)
        
        try:
            # Generate executive summary
            TaskProgress.update_progress(task_id, 20, 100, "Generating executive summary")
            summary = await analysis_workflows.generate_executive_summary(
                document.content,
                document.metadata
            )
            
            # Extract key terms and entities
            TaskProgress.update_progress(task_id, 35, 100, "Extracting key terms")
            key_terms = await analysis_workflows.extract_key_terms(document.content)
            
            # Identify risks
            TaskProgress.update_progress(task_id, 50, 100, "Identifying risks")
            risks = await analysis_workflows.identify_risks(document.content, document.metadata)
            
            # Extract obligations
            TaskProgress.update_progress(task_id, 65, 100, "Extracting obligations")
            obligations = await analysis_workflows.extract_obligations(document.content)
            
            # Calculate complexity score
            TaskProgress.update_progress(task_id, 80, 100, "Calculating complexity score")
            complexity = await analysis_workflows.calculate_complexity_score(
                document.content,
                document.metadata
            )
            
            # Create analysis results
            TaskProgress.update_progress(task_id, 90, 100, "Saving analysis results")
            
            analysis_results = AnalysisResults(
                document_id=document_id,
                summary=summary,
                key_terms=key_terms,
                risks=risks,
                obligations=obligations,
                complexity_score=complexity,
                status=AnalysisStatus.COMPLETED
            )
            
            session.add(analysis_results)
            await session.commit()
            
            TaskProgress.update_progress(task_id, 100, 100, "AI analysis completed")
            
            result = {
                "document_id": document_id,
                "analysis_id": analysis_results.id,
                "status": "success",
                "summary_length": len(summary.get("content", "")),
                "risks_found": len(risks),
                "obligations_found": len(obligations),
                "complexity_score": complexity.get("score", 0),
                "key_terms_count": len(key_terms),
            }
            
            # Notify completion
            await TaskProgress.notify_completion(task_id, result)
            
            return result
            
        except Exception as exc:
            # Create failed analysis record
            analysis_results = AnalysisResults(
                document_id=document_id,
                status=AnalysisStatus.FAILED,
                error_message=str(exc)
            )
            session.add(analysis_results)
            await session.commit()
            raise exc


@celery_app.task(bind=True, name="generate_document_summary")
def generate_document_summary_task(
    self, 
    document_id: str, 
    summary_type: str = "executive"
) -> Dict[str, Any]:
    """
    Generate a summary for a document.
    
    Args:
        document_id: The ID of the document to summarize
        summary_type: Type of summary to generate (executive, technical, legal)
        
    Returns:
        Dict containing summary results
    """
    task_id = self.request.id
    logger.info(f"Generating {summary_type} summary for document {document_id}")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, f"Starting {summary_type} summary generation")
        
        # Run async summary generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _generate_summary_async(document_id, summary_type, task_id)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Summary generation failed for document {document_id}: {exc}")
        raise AIAnalysisError(f"Failed to generate summary: {str(exc)}")


async def _generate_summary_async(
    document_id: str, 
    summary_type: str, 
    task_id: str
) -> Dict[str, Any]:
    """Async summary generation implementation."""
    
    async with AsyncSessionLocal() as session:
        # Get document
        TaskProgress.update_progress(task_id, 10, 100, "Loading document")
        
        document = await session.get(Document, document_id)
        if not document or not document.content:
            raise AIAnalysisError(f"Document {document_id} not found or has no content")
        
        # Initialize AI components
        TaskProgress.update_progress(task_id, 30, 100, "Initializing AI engine")
        llm_orchestrator = LLMOrchestrator()
        analysis_workflows = AnalysisWorkflows(llm_orchestrator)
        
        # Generate summary based on type
        TaskProgress.update_progress(task_id, 50, 100, f"Generating {summary_type} summary")
        
        if summary_type == "executive":
            summary = await analysis_workflows.generate_executive_summary(
                document.content, 
                document.metadata
            )
        elif summary_type == "technical":
            summary = await analysis_workflows.generate_technical_summary(
                document.content,
                document.metadata
            )
        elif summary_type == "legal":
            summary = await analysis_workflows.generate_legal_summary(
                document.content,
                document.metadata
            )
        else:
            raise AIAnalysisError(f"Unknown summary type: {summary_type}")
        
        TaskProgress.update_progress(task_id, 100, 100, "Summary generation completed")
        
        return {
            "document_id": document_id,
            "summary_type": summary_type,
            "summary": summary,
            "word_count": len(summary.get("content", "").split()),
            "status": "success",
        }


@celery_app.task(bind=True, name="extract_document_entities")
def extract_document_entities_task(self, document_id: str) -> Dict[str, Any]:
    """
    Extract entities from a document.
    
    Args:
        document_id: The ID of the document to process
        
    Returns:
        Dict containing extracted entities
    """
    task_id = self.request.id
    logger.info(f"Extracting entities from document {document_id}")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting entity extraction")
        
        # Run async entity extraction
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _extract_entities_async(document_id, task_id)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Entity extraction failed for document {document_id}: {exc}")
        raise AIAnalysisError(f"Failed to extract entities: {str(exc)}")


async def _extract_entities_async(document_id: str, task_id: str) -> Dict[str, Any]:
    """Async entity extraction implementation."""
    
    async with AsyncSessionLocal() as session:
        # Get document
        TaskProgress.update_progress(task_id, 10, 100, "Loading document")
        
        document = await session.get(Document, document_id)
        if not document or not document.content:
            raise AIAnalysisError(f"Document {document_id} not found or has no content")
        
        # Initialize AI components
        TaskProgress.update_progress(task_id, 30, 100, "Initializing AI engine")
        llm_orchestrator = LLMOrchestrator()
        analysis_workflows = AnalysisWorkflows(llm_orchestrator)
        
        # Extract different types of entities
        TaskProgress.update_progress(task_id, 50, 100, "Extracting key terms")
        key_terms = await analysis_workflows.extract_key_terms(document.content)
        
        TaskProgress.update_progress(task_id, 70, 100, "Extracting legal entities")
        legal_entities = await analysis_workflows.extract_legal_entities(document.content)
        
        TaskProgress.update_progress(task_id, 90, 100, "Extracting dates and amounts")
        dates_amounts = await analysis_workflows.extract_dates_and_amounts(document.content)
        
        TaskProgress.update_progress(task_id, 100, 100, "Entity extraction completed")
        
        return {
            "document_id": document_id,
            "key_terms": key_terms,
            "legal_entities": legal_entities,
            "dates_and_amounts": dates_amounts,
            "total_entities": len(key_terms) + len(legal_entities) + len(dates_amounts),
            "status": "success",
        }


@celery_app.task(bind=True, name="create_document_embeddings")
def create_document_embeddings_task(self, document_id: str) -> Dict[str, Any]:
    """
    Create embeddings for a document and store in vector database.
    
    Args:
        document_id: The ID of the document to process
        
    Returns:
        Dict containing embedding creation results
    """
    task_id = self.request.id
    logger.info(f"Creating embeddings for document {document_id}")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting embedding creation")
        
        # Run async embedding creation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _create_embeddings_async(document_id, task_id)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Embedding creation failed for document {document_id}: {exc}")
        raise AIAnalysisError(f"Failed to create embeddings: {str(exc)}")


async def _create_embeddings_async(document_id: str, task_id: str) -> Dict[str, Any]:
    """Async embedding creation implementation."""
    
    async with AsyncSessionLocal() as session:
        # Get document
        TaskProgress.update_progress(task_id, 10, 100, "Loading document")
        
        document = await session.get(Document, document_id)
        if not document or not document.content:
            raise AIAnalysisError(f"Document {document_id} not found or has no content")
        
        # Initialize vector store
        TaskProgress.update_progress(task_id, 30, 100, "Initializing vector store")
        vector_store = VectorStoreManager()
        
        # Create and store embeddings
        TaskProgress.update_progress(task_id, 50, 100, "Creating document embeddings")
        
        result = await vector_store.add_document(
            document_id=document_id,
            content=document.content,
            metadata=document.metadata
        )
        
        TaskProgress.update_progress(task_id, 100, 100, "Embedding creation completed")
        
        return {
            "document_id": document_id,
            "chunks_created": result.get("chunks_created", 0),
            "embeddings_stored": result.get("embeddings_stored", 0),
            "status": "success",
        }


@celery_app.task(bind=True, name="comprehensive_document_analysis")
def comprehensive_document_analysis_task(
    self, 
    document_id: str, 
    user_id: str,
    analysis_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Perform comprehensive document analysis with all AI workflows.
    
    Args:
        document_id: The ID of the document to analyze
        user_id: User requesting the analysis
        analysis_options: Additional analysis configuration options
        
    Returns:
        Dict containing comprehensive analysis results
    """
    task_id = self.request.id
    logger.info(f"Starting comprehensive analysis for document {document_id}")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting comprehensive analysis")
        
        # Run async comprehensive analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _comprehensive_analysis_async(document_id, user_id, task_id, analysis_options)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Comprehensive analysis failed for document {document_id}: {exc}")
        raise AIAnalysisError(f"Failed to perform comprehensive analysis: {str(exc)}")


async def _comprehensive_analysis_async(
    document_id: str, 
    user_id: str, 
    task_id: str,
    analysis_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Async comprehensive analysis implementation."""
    
    async with AsyncSessionLocal() as session:
        # Get document from database
        TaskProgress.update_progress(task_id, 5, 100, "Loading document from database")
        
        document = await session.get(Document, document_id)
        if not document:
            raise AIAnalysisError(f"Document {document_id} not found")
        
        if not document.content:
            raise AIAnalysisError(f"Document {document_id} has no content to analyze")
        
        # Initialize AI components
        TaskProgress.update_progress(task_id, 10, 100, "Initializing AI analysis workflow")
        
        from app.core.ai.llm_orchestrator import LLMOrchestrator
        from app.core.ai.analysis_workflows import DocumentAnalysisWorkflow, AnalysisWorkflowType
        
        llm_orchestrator = LLMOrchestrator()
        analysis_workflow = DocumentAnalysisWorkflow(llm_orchestrator)
        
        try:
            # Perform comprehensive analysis
            TaskProgress.update_progress(task_id, 20, 100, "Executing comprehensive analysis workflow")
            
            analysis_results = await analysis_workflow.analyze_document(
                document_content=document.content,
                document_type=document.document_type or "unknown",
                workflow_type=AnalysisWorkflowType.FULL_ANALYSIS,
                user_jurisdiction_hint=analysis_options.get("jurisdiction_hint") if analysis_options else None,
                additional_context={
                    "document_id": document_id,
                    "user_id": user_id,
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    **(analysis_options or {})
                }
            )
            
            # Create comprehensive analysis results record
            TaskProgress.update_progress(task_id, 90, 100, "Saving comprehensive analysis results")
            
            from app.database.models.analysis import AnalysisResults
            from app.schemas.analysis import AnalysisStatus
            
            comprehensive_analysis = AnalysisResults(
                document_id=document_id,
                summary=analysis_results.get("document_analysis", {}).get("executive_summary", {}),
                key_terms=analysis_results.get("document_analysis", {}).get("key_terms", []),
                risks=analysis_results.get("document_analysis", {}).get("risk_analysis", {}).get("risks", []),
                obligations=analysis_results.get("document_analysis", {}).get("obligation_extraction", {}).get("obligations", []),
                complexity_score=analysis_results.get("document_analysis", {}).get("complexity_scoring", {}),
                jurisdiction_analysis=analysis_results.get("jurisdiction_analysis", {}),
                jurisdiction_specific_analysis=analysis_results.get("jurisdiction_specific", {}),
                status=AnalysisStatus.COMPLETED,
                metadata=analysis_results.get("metadata", {})
            )
            
            session.add(comprehensive_analysis)
            await session.commit()
            
            TaskProgress.update_progress(task_id, 100, 100, "Comprehensive analysis completed")
            
            result = {
                "document_id": document_id,
                "analysis_id": comprehensive_analysis.id,
                "status": "success",
                "analysis_results": analysis_results,
                "processing_time_seconds": analysis_results.get("metadata", {}).get("processing_time_seconds"),
                "jurisdiction": analysis_results.get("jurisdiction_analysis", {}).get("primary_jurisdiction"),
                "risks_found": len(analysis_results.get("document_analysis", {}).get("risk_analysis", {}).get("risks", [])),
                "obligations_found": len(analysis_results.get("document_analysis", {}).get("obligation_extraction", {}).get("obligations", [])),
                "complexity_score": analysis_results.get("document_analysis", {}).get("complexity_scoring", {}).get("score", 0),
            }
            
            # Notify completion
            await TaskProgress.notify_completion(task_id, result)
            
            return result
            
        except Exception as exc:
            # Create failed analysis record
            from app.database.models.analysis import AnalysisResults
            from app.schemas.analysis import AnalysisStatus
            
            failed_analysis = AnalysisResults(
                document_id=document_id,
                status=AnalysisStatus.FAILED,
                error_message=str(exc),
                metadata={"task_id": task_id, "user_id": user_id}
            )
            session.add(failed_analysis)
            await session.commit()
            raise exc


@celery_app.task(bind=True, name="jurisdiction_specific_analysis")
def jurisdiction_specific_analysis_task(
    self,
    document_id: str,
    jurisdiction: str,
    analysis_type: str,
    user_id: str,
    parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Perform jurisdiction-specific analysis (stamp duty, UCC, etc.).
    
    Args:
        document_id: The ID of the document to analyze
        jurisdiction: Legal jurisdiction (india, usa, cross_border)
        analysis_type: Specific analysis type
        user_id: User requesting the analysis
        parameters: Additional parameters for analysis
        
    Returns:
        Dict containing jurisdiction-specific analysis results
    """
    task_id = self.request.id
    logger.info(f"Starting {jurisdiction} {analysis_type} analysis for document {document_id}")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, f"Starting {jurisdiction} {analysis_type} analysis")
        
        # Run async jurisdiction-specific analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _jurisdiction_specific_analysis_async(
                    document_id, jurisdiction, analysis_type, user_id, task_id, parameters
                )
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Jurisdiction-specific analysis failed for document {document_id}: {exc}")
        raise AIAnalysisError(f"Failed to perform {jurisdiction} {analysis_type}: {str(exc)}")


async def _jurisdiction_specific_analysis_async(
    document_id: str,
    jurisdiction: str,
    analysis_type: str,
    user_id: str,
    task_id: str,
    parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Async jurisdiction-specific analysis implementation."""
    
    async with AsyncSessionLocal() as session:
        # Get document
        TaskProgress.update_progress(task_id, 10, 100, "Loading document")
        
        document = await session.get(Document, document_id)
        if not document or not document.content:
            raise AIAnalysisError(f"Document {document_id} not found or has no content")
        
        # Initialize AI components
        TaskProgress.update_progress(task_id, 30, 100, "Initializing jurisdiction-specific processors")
        
        from app.services.ai_analysis_service import AIAnalysisService
        
        ai_service = AIAnalysisService()
        
        # Perform jurisdiction-specific analysis
        TaskProgress.update_progress(task_id, 50, 100, f"Executing {jurisdiction} {analysis_type} analysis")
        
        results = await ai_service.analyze_jurisdiction_specific(
            document_content=document.content,
            document_type=document.document_type or "unknown",
            jurisdiction=jurisdiction,
            analysis_type=analysis_type,
            **(parameters or {})
        )
        
        # Store results in database
        TaskProgress.update_progress(task_id, 90, 100, "Saving jurisdiction-specific analysis results")
        
        from app.database.models.analysis import JurisdictionAnalysis
        
        jurisdiction_analysis = JurisdictionAnalysis(
            document_id=document_id,
            jurisdiction=jurisdiction,
            analysis_type=analysis_type,
            results=results,
            parameters=parameters or {},
            user_id=user_id,
            task_id=task_id
        )
        
        session.add(jurisdiction_analysis)
        await session.commit()
        
        TaskProgress.update_progress(task_id, 100, 100, f"{jurisdiction} {analysis_type} analysis completed")
        
        return {
            "document_id": document_id,
            "jurisdiction": jurisdiction,
            "analysis_type": analysis_type,
            "analysis_id": jurisdiction_analysis.id,
            "results": results,
            "status": "success",
        }


@celery_app.task(bind=True, name="batch_document_analysis")
def batch_document_analysis_task(
    self,
    document_ids: List[str],
    analysis_type: str,
    user_id: str,
    batch_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Perform batch analysis on multiple documents.
    
    Args:
        document_ids: List of document IDs to analyze
        analysis_type: Type of analysis to perform
        user_id: User requesting the analysis
        batch_options: Additional batch processing options
        
    Returns:
        Dict containing batch analysis results
    """
    task_id = self.request.id
    logger.info(f"Starting batch {analysis_type} analysis for {len(document_ids)} documents")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, f"Starting batch analysis of {len(document_ids)} documents")
        
        # Run async batch analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _batch_analysis_async(document_ids, analysis_type, user_id, task_id, batch_options)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Batch analysis failed: {exc}")
        raise AIAnalysisError(f"Failed to perform batch analysis: {str(exc)}")


async def _batch_analysis_async(
    document_ids: List[str],
    analysis_type: str,
    user_id: str,
    task_id: str,
    batch_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Async batch analysis implementation."""
    
    results = []
    failed_documents = []
    total_documents = len(document_ids)
    
    async with AsyncSessionLocal() as session:
        for i, document_id in enumerate(document_ids):
            try:
                progress = int((i / total_documents) * 90)  # Reserve 10% for final processing
                TaskProgress.update_progress(
                    task_id, progress, 100, 
                    f"Processing document {i+1}/{total_documents}: {document_id}"
                )
                
                # Get document
                document = await session.get(Document, document_id)
                if not document or not document.content:
                    failed_documents.append({
                        "document_id": document_id,
                        "error": "Document not found or has no content"
                    })
                    continue
                
                # Initialize AI service
                from app.services.ai_analysis_service import AIAnalysisService
                ai_service = AIAnalysisService()
                
                # Perform analysis based on type
                if analysis_type == "comprehensive":
                    analysis_result = await ai_service.analyze_document_comprehensive(
                        document_id=document_id,
                        document_content=document.content,
                        document_type=document.document_type or "unknown",
                        user_id=user_id,
                        analysis_options=batch_options
                    )
                else:
                    analysis_result = await ai_service.analyze_document_quick(
                        document_content=document.content,
                        document_type=document.document_type or "unknown",
                        analysis_type=analysis_type
                    )
                
                results.append({
                    "document_id": document_id,
                    "status": "success",
                    "analysis_result": analysis_result
                })
                
            except Exception as exc:
                logger.error(f"Failed to analyze document {document_id}: {exc}")
                failed_documents.append({
                    "document_id": document_id,
                    "error": str(exc)
                })
        
        TaskProgress.update_progress(task_id, 100, 100, "Batch analysis completed")
        
        return {
            "batch_id": task_id,
            "analysis_type": analysis_type,
            "total_documents": total_documents,
            "successful_analyses": len(results),
            "failed_analyses": len(failed_documents),
            "results": results,
            "failed_documents": failed_documents,
            "status": "completed",
        }