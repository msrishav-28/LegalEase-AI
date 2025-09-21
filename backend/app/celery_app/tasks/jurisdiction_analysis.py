"""Jurisdiction analysis tasks for Celery workers."""

import asyncio
import logging
from typing import Dict, Any, Optional
from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app.celery import celery_app, TaskProgress, JurisdictionAnalysisError
from app.database.connection import AsyncSessionLocal
from app.core.jurisdiction.detector import JurisdictionDetector
from app.core.jurisdiction.indian_processor import IndianLegalProcessor
from app.core.jurisdiction.us_processor import USLegalProcessor
from app.core.jurisdiction.comparative_analyzer import ComparativeJurisdictionAnalyzer
from app.database.models import Document, JurisdictionAnalysis
from app.database.models.analysis import JurisdictionType

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="detect_document_jurisdiction")
def detect_document_jurisdiction_task(self, document_id: str) -> Dict[str, Any]:
    """
    Detect the jurisdiction of a document.
    
    Args:
        document_id: The ID of the document to analyze
        
    Returns:
        Dict containing jurisdiction detection results
    """
    task_id = self.request.id
    logger.info(f"Starting jurisdiction detection for document {document_id}")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting jurisdiction detection")
        
        # Run async detection in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _detect_jurisdiction_async(document_id, task_id)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Jurisdiction detection failed for document {document_id}: {exc}")
        raise JurisdictionAnalysisError(f"Failed to detect jurisdiction: {str(exc)}")


async def _detect_jurisdiction_async(document_id: str, task_id: str) -> Dict[str, Any]:
    """Async jurisdiction detection implementation."""
    
    async with AsyncSessionLocal() as session:
        # Get document from database
        TaskProgress.update_progress(task_id, 10, 100, "Loading document from database")
        
        document = await session.get(Document, document_id)
        if not document:
            raise JurisdictionAnalysisError(f"Document {document_id} not found")
        
        if not document.content:
            raise JurisdictionAnalysisError(f"Document {document_id} has no content to analyze")
        
        # Initialize jurisdiction detector
        TaskProgress.update_progress(task_id, 30, 100, "Initializing jurisdiction detector")
        detector = JurisdictionDetector()
        
        # Detect jurisdiction
        TaskProgress.update_progress(task_id, 60, 100, "Detecting jurisdiction")
        detection_result = await detector.detect_jurisdiction(document.content)
        
        # Update document metadata with jurisdiction info
        TaskProgress.update_progress(task_id, 80, 100, "Updating document metadata")
        
        document.metadata = {
            **document.metadata,
            "jurisdiction": detection_result.jurisdiction.value,
            "jurisdiction_confidence": detection_result.confidence,
            "jurisdiction_scores": detection_result.scores,
            "detected_elements": detection_result.detected_elements,
        }
        
        if detection_result.us_state:
            document.metadata["us_state"] = detection_result.us_state
        
        await session.commit()
        
        TaskProgress.update_progress(task_id, 100, 100, "Jurisdiction detection completed")
        
        return {
            "document_id": document_id,
            "jurisdiction": detection_result.jurisdiction.value,
            "confidence": detection_result.confidence,
            "scores": detection_result.scores,
            "us_state": detection_result.us_state,
            "detected_elements": detection_result.detected_elements,
            "status": "success",
        }


@celery_app.task(bind=True, name="analyze_indian_legal_document")
def analyze_indian_legal_document_task(self, document_id: str) -> Dict[str, Any]:
    """
    Perform Indian legal system analysis on a document.
    
    Args:
        document_id: The ID of the document to analyze
        
    Returns:
        Dict containing Indian legal analysis results
    """
    task_id = self.request.id
    logger.info(f"Starting Indian legal analysis for document {document_id}")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting Indian legal analysis")
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _analyze_indian_legal_async(document_id, task_id)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Indian legal analysis failed for document {document_id}: {exc}")
        raise JurisdictionAnalysisError(f"Failed to analyze Indian legal document: {str(exc)}")


async def _analyze_indian_legal_async(document_id: str, task_id: str) -> Dict[str, Any]:
    """Async Indian legal analysis implementation."""
    
    async with AsyncSessionLocal() as session:
        # Get document
        TaskProgress.update_progress(task_id, 10, 100, "Loading document")
        
        document = await session.get(Document, document_id)
        if not document or not document.content:
            raise JurisdictionAnalysisError(f"Document {document_id} not found or has no content")
        
        # Initialize Indian legal processor
        TaskProgress.update_progress(task_id, 20, 100, "Initializing Indian legal processor")
        processor = IndianLegalProcessor()
        
        # Analyze Indian acts compliance
        TaskProgress.update_progress(task_id, 40, 100, "Analyzing Indian acts compliance")
        acts_analysis = await processor.analyze_acts_compliance(document.content)
        
        # Calculate stamp duty
        TaskProgress.update_progress(task_id, 60, 100, "Calculating stamp duty requirements")
        stamp_duty = await processor.calculate_stamp_duty(
            document.content,
            document.metadata.get("document_type", "contract")
        )
        
        # Analyze GST implications
        TaskProgress.update_progress(task_id, 80, 100, "Analyzing GST implications")
        gst_analysis = await processor.analyze_gst_implications(document.content)
        
        # Create jurisdiction analysis record
        TaskProgress.update_progress(task_id, 90, 100, "Saving analysis results")
        
        jurisdiction_analysis = JurisdictionAnalysis(
            document_id=document_id,
            jurisdiction=JurisdictionType.INDIA,
            analysis_results={
                "acts_compliance": acts_analysis,
                "stamp_duty": stamp_duty,
                "gst_analysis": gst_analysis,
            }
        )
        
        session.add(jurisdiction_analysis)
        await session.commit()
        
        TaskProgress.update_progress(task_id, 100, 100, "Indian legal analysis completed")
        
        return {
            "document_id": document_id,
            "analysis_id": jurisdiction_analysis.id,
            "jurisdiction": "INDIA",
            "acts_found": len(acts_analysis.get("applicable_acts", [])),
            "stamp_duty_amount": stamp_duty.get("amount", 0),
            "gst_applicable": gst_analysis.get("applicable", False),
            "status": "success",
        }


@celery_app.task(bind=True, name="analyze_us_legal_document")
def analyze_us_legal_document_task(self, document_id: str) -> Dict[str, Any]:
    """
    Perform US legal system analysis on a document.
    
    Args:
        document_id: The ID of the document to analyze
        
    Returns:
        Dict containing US legal analysis results
    """
    task_id = self.request.id
    logger.info(f"Starting US legal analysis for document {document_id}")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting US legal analysis")
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _analyze_us_legal_async(document_id, task_id)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"US legal analysis failed for document {document_id}: {exc}")
        raise JurisdictionAnalysisError(f"Failed to analyze US legal document: {str(exc)}")


async def _analyze_us_legal_async(document_id: str, task_id: str) -> Dict[str, Any]:
    """Async US legal analysis implementation."""
    
    async with AsyncSessionLocal() as session:
        # Get document
        TaskProgress.update_progress(task_id, 10, 100, "Loading document")
        
        document = await session.get(Document, document_id)
        if not document or not document.content:
            raise JurisdictionAnalysisError(f"Document {document_id} not found or has no content")
        
        # Initialize US legal processor
        TaskProgress.update_progress(task_id, 20, 100, "Initializing US legal processor")
        processor = USLegalProcessor()
        
        # Analyze federal regulations
        TaskProgress.update_progress(task_id, 40, 100, "Analyzing federal regulations")
        federal_analysis = await processor.analyze_federal_regulations(document.content)
        
        # Analyze UCC compliance
        TaskProgress.update_progress(task_id, 60, 100, "Analyzing UCC compliance")
        ucc_analysis = await processor.analyze_ucc_compliance(document.content)
        
        # Analyze securities compliance
        TaskProgress.update_progress(task_id, 80, 100, "Analyzing securities compliance")
        securities_analysis = await processor.analyze_securities_compliance(document.content)
        
        # Create jurisdiction analysis record
        TaskProgress.update_progress(task_id, 90, 100, "Saving analysis results")
        
        jurisdiction_analysis = JurisdictionAnalysis(
            document_id=document_id,
            jurisdiction=JurisdictionType.USA,
            analysis_results={
                "federal_regulations": federal_analysis,
                "ucc_compliance": ucc_analysis,
                "securities_compliance": securities_analysis,
            }
        )
        
        session.add(jurisdiction_analysis)
        await session.commit()
        
        TaskProgress.update_progress(task_id, 100, 100, "US legal analysis completed")
        
        return {
            "document_id": document_id,
            "analysis_id": jurisdiction_analysis.id,
            "jurisdiction": "USA",
            "federal_regulations_found": len(federal_analysis.get("applicable_regulations", [])),
            "ucc_applicable": ucc_analysis.get("applicable", False),
            "securities_compliant": securities_analysis.get("compliant", True),
            "status": "success",
        }


@celery_app.task(bind=True, name="perform_cross_border_analysis")
def perform_cross_border_analysis_task(self, document_id: str) -> Dict[str, Any]:
    """
    Perform cross-border legal analysis comparing Indian and US requirements.
    
    Args:
        document_id: The ID of the document to analyze
        
    Returns:
        Dict containing cross-border analysis results
    """
    task_id = self.request.id
    logger.info(f"Starting cross-border analysis for document {document_id}")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting cross-border analysis")
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _perform_cross_border_analysis_async(document_id, task_id)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Cross-border analysis failed for document {document_id}: {exc}")
        raise JurisdictionAnalysisError(f"Failed to perform cross-border analysis: {str(exc)}")


async def _perform_cross_border_analysis_async(document_id: str, task_id: str) -> Dict[str, Any]:
    """Async cross-border analysis implementation."""
    
    async with AsyncSessionLocal() as session:
        # Get document
        TaskProgress.update_progress(task_id, 10, 100, "Loading document")
        
        document = await session.get(Document, document_id)
        if not document or not document.content:
            raise JurisdictionAnalysisError(f"Document {document_id} not found or has no content")
        
        # Initialize comparative analyzer
        TaskProgress.update_progress(task_id, 20, 100, "Initializing comparative analyzer")
        analyzer = ComparativeJurisdictionAnalyzer()
        
        # Perform enforceability comparison
        TaskProgress.update_progress(task_id, 40, 100, "Analyzing enforceability comparison")
        enforceability = await analyzer.compare_enforceability(document.content)
        
        # Compare formalities
        TaskProgress.update_progress(task_id, 60, 100, "Comparing legal formalities")
        formalities = await analyzer.compare_formalities(document.content)
        
        # Analyze tax implications
        TaskProgress.update_progress(task_id, 80, 100, "Analyzing tax implications")
        tax_implications = await analyzer.analyze_tax_implications(document.content)
        
        # Create jurisdiction analysis record
        TaskProgress.update_progress(task_id, 90, 100, "Saving analysis results")
        
        jurisdiction_analysis = JurisdictionAnalysis(
            document_id=document_id,
            jurisdiction=JurisdictionType.CROSS_BORDER,
            analysis_results={
                "enforceability_comparison": enforceability,
                "formalities_comparison": formalities,
                "tax_implications": tax_implications,
            }
        )
        
        session.add(jurisdiction_analysis)
        await session.commit()
        
        TaskProgress.update_progress(task_id, 100, 100, "Cross-border analysis completed")
        
        return {
            "document_id": document_id,
            "analysis_id": jurisdiction_analysis.id,
            "jurisdiction": "CROSS_BORDER",
            "enforceability_score": enforceability.get("overall_score", 0),
            "formalities_differences": len(formalities.get("differences", [])),
            "tax_complexity": tax_implications.get("complexity_score", 0),
            "status": "success",
        }


@celery_app.task(bind=True, name="comprehensive_jurisdiction_analysis")
def comprehensive_jurisdiction_analysis_task(self, document_id: str) -> Dict[str, Any]:
    """
    Perform comprehensive jurisdiction analysis including detection and jurisdiction-specific analysis.
    
    Args:
        document_id: The ID of the document to analyze
        
    Returns:
        Dict containing comprehensive analysis results
    """
    task_id = self.request.id
    logger.info(f"Starting comprehensive jurisdiction analysis for document {document_id}")
    
    try:
        TaskProgress.update_progress(task_id, 0, 100, "Starting comprehensive analysis")
        
        # Step 1: Detect jurisdiction
        TaskProgress.update_progress(task_id, 10, 100, "Detecting jurisdiction")
        detection_result = detect_document_jurisdiction_task.delay(document_id)
        detection_data = detection_result.get()
        
        if detection_data["status"] != "success":
            raise JurisdictionAnalysisError("Jurisdiction detection failed")
        
        jurisdiction = detection_data["jurisdiction"]
        
        # Step 2: Perform jurisdiction-specific analysis
        if jurisdiction == "INDIA":
            TaskProgress.update_progress(task_id, 50, 100, "Performing Indian legal analysis")
            analysis_result = analyze_indian_legal_document_task.delay(document_id)
            analysis_data = analysis_result.get()
            
        elif jurisdiction == "USA":
            TaskProgress.update_progress(task_id, 50, 100, "Performing US legal analysis")
            analysis_result = analyze_us_legal_document_task.delay(document_id)
            analysis_data = analysis_result.get()
            
        else:  # Cross-border or unknown
            TaskProgress.update_progress(task_id, 50, 100, "Performing cross-border analysis")
            analysis_result = perform_cross_border_analysis_task.delay(document_id)
            analysis_data = analysis_result.get()
        
        TaskProgress.update_progress(task_id, 100, 100, "Comprehensive analysis completed")
        
        return {
            "document_id": document_id,
            "jurisdiction_detection": detection_data,
            "jurisdiction_analysis": analysis_data,
            "status": "success",
        }
        
    except Exception as exc:
        logger.error(f"Comprehensive jurisdiction analysis failed for document {document_id}: {exc}")
        raise JurisdictionAnalysisError(f"Failed to perform comprehensive analysis: {str(exc)}")