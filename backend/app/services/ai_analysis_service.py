"""AI Analysis Service for coordinating document analysis workflows."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.ai.llm_orchestrator import LLMOrchestrator
from app.core.ai.analysis_workflows import DocumentAnalysisWorkflow, AnalysisWorkflowType
from app.core.ai.prompt_templates import JurisdictionType
from app.core.jurisdiction.detector import JurisdictionDetector
from app.core.jurisdiction.indian_processor import IndianLegalProcessor
from app.core.jurisdiction.us_processor import USLegalProcessor
from app.core.jurisdiction.comparative_analyzer import ComparativeJurisdictionAnalyzer
from app.core.exceptions import AIProcessingError, InvalidInputError
from app.config import get_settings


logger = logging.getLogger(__name__)


class AIAnalysisService:
    """
    Service layer for AI-powered document analysis.
    Coordinates between different analysis components and provides a unified interface.
    """
    
    def __init__(self):
        """Initialize the AI analysis service with all required components."""
        settings = get_settings()
        
        # Initialize LLM orchestrator
        self.llm_orchestrator = LLMOrchestrator(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=settings.ai_temperature,
            max_tokens=settings.openai_max_tokens
        )
        
        # Initialize jurisdiction processors
        self.jurisdiction_detector = JurisdictionDetector()
        self.indian_processor = IndianLegalProcessor()
        self.us_processor = USLegalProcessor()
        self.comparative_analyzer = ComparativeJurisdictionAnalyzer()
        
        # Initialize analysis workflow
        self.analysis_workflow = DocumentAnalysisWorkflow(
            llm_orchestrator=self.llm_orchestrator,
            jurisdiction_detector=self.jurisdiction_detector,
            indian_processor=self.indian_processor,
            us_processor=self.us_processor,
            comparative_analyzer=self.comparative_analyzer
        )
    
    async def analyze_document_comprehensive(
        self,
        document_id: str,
        document_content: str,
        document_type: str,
        user_id: str,
        jurisdiction_hint: Optional[str] = None,
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive document analysis with jurisdiction awareness.
        
        Args:
            document_id: Unique document identifier
            document_content: The document text to analyze
            document_type: Type of document (contract, agreement, etc.)
            user_id: User requesting the analysis
            jurisdiction_hint: Optional jurisdiction hint from user
            analysis_options: Additional analysis configuration options
            
        Returns:
            Comprehensive analysis results
        """
        try:
            logger.info(f"Starting comprehensive analysis for document {document_id}")
            
            # Prepare analysis context
            context = {
                "document_id": document_id,
                "user_id": user_id,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                **(analysis_options or {})
            }
            
            # Execute comprehensive analysis workflow
            analysis_results = await self.analysis_workflow.analyze_document(
                document_content=document_content,
                document_type=document_type,
                workflow_type=AnalysisWorkflowType.FULL_ANALYSIS,
                user_jurisdiction_hint=jurisdiction_hint,
                additional_context=context
            )
            
            # Generate executive summary with jurisdiction context
            executive_summary = await self.analysis_workflow.generate_executive_summary_with_jurisdiction_context(
                document_content=document_content,
                document_type=document_type,
                jurisdiction_analysis=analysis_results["jurisdiction_analysis"],
                full_analysis_results=analysis_results["document_analysis"]
            )
            
            # Add executive summary to results
            analysis_results["executive_summary"] = executive_summary
            
            logger.info(f"Completed comprehensive analysis for document {document_id}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed for document {document_id}: {str(e)}")
            raise AIProcessingError(f"Failed to analyze document: {str(e)}")
    
    async def analyze_document_quick(
        self,
        document_content: str,
        document_type: str,
        analysis_type: str = "executive_summary",
        jurisdiction_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform quick document analysis for specific analysis type.
        
        Args:
            document_content: The document text to analyze
            document_type: Type of document
            analysis_type: Specific analysis type to perform
            jurisdiction_hint: Optional jurisdiction hint
            
        Returns:
            Quick analysis results
        """
        try:
            # Map analysis type to workflow type
            workflow_type_map = {
                "executive_summary": AnalysisWorkflowType.EXECUTIVE_SUMMARY,
                "risk_analysis": AnalysisWorkflowType.RISK_ANALYSIS,
                "obligation_extraction": AnalysisWorkflowType.OBLIGATION_EXTRACTION,
                "complexity_scoring": AnalysisWorkflowType.COMPLEXITY_SCORING,
                "jurisdiction_analysis": AnalysisWorkflowType.JURISDICTION_ANALYSIS,
                "compliance_check": AnalysisWorkflowType.COMPLIANCE_CHECK
            }
            
            workflow_type = workflow_type_map.get(analysis_type, AnalysisWorkflowType.EXECUTIVE_SUMMARY)
            
            # Execute specific analysis workflow
            results = await self.analysis_workflow.analyze_document(
                document_content=document_content,
                document_type=document_type,
                workflow_type=workflow_type,
                user_jurisdiction_hint=jurisdiction_hint
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Quick analysis failed: {str(e)}")
            raise AIProcessingError(f"Failed to perform {analysis_type}: {str(e)}")
    
    async def chat_with_document(
        self,
        session_id: str,
        question: str,
        document_content: Optional[str] = None,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
        jurisdiction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Interactive chat about a document with AI assistance.
        
        Args:
            session_id: Conversation session ID
            question: User's question about the document
            document_content: Document text (if not in session)
            document_id: Document identifier
            user_id: User identifier
            jurisdiction: Legal jurisdiction context
            
        Returns:
            Chat response with contextual information
        """
        try:
            # Convert jurisdiction string to enum
            jurisdiction_type = None
            if jurisdiction:
                try:
                    jurisdiction_type = JurisdictionType(jurisdiction.lower())
                except ValueError:
                    jurisdiction_type = JurisdictionType.UNKNOWN
            
            # Use LLM orchestrator for chat
            response = await self.llm_orchestrator.chat_with_document(
                session_id=session_id,
                question=question,
                document_content=document_content,
                jurisdiction=jurisdiction_type,
                user_id=user_id
            )
            
            # Add document context if available
            if document_id:
                response["document_id"] = document_id
            
            return response
            
        except Exception as e:
            logger.error(f"Chat interaction failed: {str(e)}")
            raise AIProcessingError(f"Failed to process chat: {str(e)}")
    
    async def stream_chat_response(
        self,
        session_id: str,
        question: str,
        document_content: Optional[str] = None,
        user_id: Optional[str] = None,
        jurisdiction: Optional[str] = None
    ):
        """
        Stream chat response for real-time interaction.
        
        Args:
            session_id: Conversation session ID
            question: User's question
            document_content: Document text
            user_id: User identifier
            jurisdiction: Legal jurisdiction context
            
        Yields:
            Streaming response chunks
        """
        try:
            # Convert jurisdiction string to enum
            jurisdiction_type = None
            if jurisdiction:
                try:
                    jurisdiction_type = JurisdictionType(jurisdiction.lower())
                except ValueError:
                    jurisdiction_type = JurisdictionType.UNKNOWN
            
            # Stream response from LLM orchestrator
            async for chunk in self.llm_orchestrator.stream_chat_response(
                session_id=session_id,
                question=question,
                document_content=document_content,
                jurisdiction=jurisdiction_type,
                user_id=user_id
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"Streaming chat failed: {str(e)}")
            yield f"Error: {str(e)}"
    
    async def analyze_jurisdiction_specific(
        self,
        document_content: str,
        document_type: str,
        jurisdiction: str,
        analysis_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform jurisdiction-specific analysis (stamp duty, UCC, etc.).
        
        Args:
            document_content: Document text
            document_type: Type of document
            jurisdiction: Legal jurisdiction
            analysis_type: Specific analysis type
            **kwargs: Additional parameters
            
        Returns:
            Jurisdiction-specific analysis results
        """
        try:
            # Convert jurisdiction string to enum
            jurisdiction_type = JurisdictionType(jurisdiction.lower())
            
            # Use LLM orchestrator for jurisdiction-specific analysis
            results = await self.llm_orchestrator.analyze_jurisdiction_specific(
                document_content=document_content,
                jurisdiction=jurisdiction_type,
                analysis_type=analysis_type,
                document_type=document_type,
                **kwargs
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Jurisdiction-specific analysis failed: {str(e)}")
            raise AIProcessingError(f"Failed to perform {analysis_type}: {str(e)}")
    
    async def compare_documents(
        self,
        document1_content: str,
        document2_content: str,
        document1_type: str,
        document2_type: str,
        comparison_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Compare two documents with AI analysis.
        
        Args:
            document1_content: First document text
            document2_content: Second document text
            document1_type: Type of first document
            document2_type: Type of second document
            comparison_type: Type of comparison to perform
            
        Returns:
            Document comparison results
        """
        try:
            # Detect jurisdictions for both documents
            jurisdiction1_task = self.analysis_workflow._detect_jurisdiction(document1_content)
            jurisdiction2_task = self.analysis_workflow._detect_jurisdiction(document2_content)
            
            jurisdiction1, jurisdiction2 = await asyncio.gather(jurisdiction1_task, jurisdiction2_task)
            
            # Prepare comparison context
            context = {
                "document1_jurisdiction": jurisdiction1,
                "document2_jurisdiction": jurisdiction2,
                "comparison_type": comparison_type
            }
            
            # Use comparative analyzer if cross-border
            if (jurisdiction1["primary_jurisdiction"] != jurisdiction2["primary_jurisdiction"] and
                jurisdiction1["primary_jurisdiction"] in ["india", "usa"] and
                jurisdiction2["primary_jurisdiction"] in ["india", "usa"]):
                
                # Cross-border comparison
                comparative_results = self.comparative_analyzer.compare_documents(
                    document1_content, document2_content
                )
                
                # Enhance with AI analysis
                ai_comparison = await self.llm_orchestrator.analyze_jurisdiction_specific(
                    document_content=f"Document 1:\n{document1_content}\n\nDocument 2:\n{document2_content}",
                    jurisdiction=JurisdictionType.CROSS_BORDER,
                    analysis_type="document_comparison",
                    document1_type=document1_type,
                    document2_type=document2_type,
                    context=context
                )
                
                return {
                    "comparison_type": "cross_border",
                    "comparative_analysis": comparative_results,
                    "ai_analysis": ai_comparison,
                    "jurisdictions": {
                        "document1": jurisdiction1,
                        "document2": jurisdiction2
                    }
                }
            else:
                # Same jurisdiction comparison
                primary_jurisdiction = JurisdictionType(jurisdiction1["primary_jurisdiction"])
                
                ai_comparison = await self.llm_orchestrator.analyze_document(
                    document_content=f"Document 1:\n{document1_content}\n\nDocument 2:\n{document2_content}",
                    document_type="comparison",
                    jurisdiction=primary_jurisdiction,
                    analysis_type="document_comparison",
                    context=context
                )
                
                return {
                    "comparison_type": "same_jurisdiction",
                    "ai_analysis": ai_comparison,
                    "jurisdiction": jurisdiction1
                }
                
        except Exception as e:
            logger.error(f"Document comparison failed: {str(e)}")
            raise AIProcessingError(f"Failed to compare documents: {str(e)}")
    
    async def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get the status of a running analysis.
        
        Args:
            analysis_id: Analysis identifier
            
        Returns:
            Analysis status information
        """
        # This would integrate with background task system (Celery)
        # For now, return a placeholder
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "progress": 100,
            "message": "Analysis completed successfully"
        }
    
    def get_supported_analysis_types(self) -> List[str]:
        """Get list of supported analysis types."""
        return [
            "executive_summary",
            "risk_analysis", 
            "obligation_extraction",
            "complexity_scoring",
            "jurisdiction_analysis",
            "compliance_check",
            "comparative_analysis",
            "full_analysis"
        ]
    
    def get_supported_jurisdictions(self) -> List[str]:
        """Get list of supported jurisdictions."""
        return [
            "india",
            "usa", 
            "cross_border",
            "unknown"
        ]
    
    def get_jurisdiction_specific_analyses(self, jurisdiction: str) -> List[str]:
        """Get jurisdiction-specific analysis types."""
        jurisdiction_analyses = {
            "india": [
                "stamp_duty_calculation",
                "gst_analysis",
                "contract_act_compliance",
                "companies_act_compliance",
                "indian_comprehensive_analysis"
            ],
            "usa": [
                "ucc_analysis",
                "securities_compliance",
                "privacy_compliance",
                "state_law_analysis",
                "us_comprehensive_analysis"
            ],
            "cross_border": [
                "enforceability_comparison",
                "tax_implications",
                "formalities_comparison",
                "cross_border_comprehensive_analysis"
            ]
        }
        
        return jurisdiction_analyses.get(jurisdiction.lower(), [])