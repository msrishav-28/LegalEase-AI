"""Jurisdiction-aware document analysis workflows."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from .llm_orchestrator import LLMOrchestrator
from .prompt_templates import JurisdictionType
from ..jurisdiction.detector import JurisdictionDetector
from ..jurisdiction.indian_processor import IndianLegalProcessor
from ..jurisdiction.us_processor import USLegalProcessor
from ..jurisdiction.comparative_analyzer import ComparativeJurisdictionAnalyzer
from ..exceptions import AIProcessingError, InvalidInputError


logger = logging.getLogger(__name__)


class AnalysisWorkflowType(str, Enum):
    """Types of analysis workflows."""
    EXECUTIVE_SUMMARY = "executive_summary"
    RISK_ANALYSIS = "risk_analysis"
    OBLIGATION_EXTRACTION = "obligation_extraction"
    COMPLEXITY_SCORING = "complexity_scoring"
    JURISDICTION_ANALYSIS = "jurisdiction_analysis"
    COMPLIANCE_CHECK = "compliance_check"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    FULL_ANALYSIS = "full_analysis"


class DocumentAnalysisWorkflow:
    """
    Orchestrates comprehensive jurisdiction-aware document analysis workflows.
    Combines AI analysis with jurisdiction-specific legal processing.
    """
    
    def __init__(
        self,
        llm_orchestrator: LLMOrchestrator,
        jurisdiction_detector: Optional[JurisdictionDetector] = None,
        indian_processor: Optional[IndianLegalProcessor] = None,
        us_processor: Optional[USLegalProcessor] = None,
        comparative_analyzer: Optional[ComparativeJurisdictionAnalyzer] = None
    ):
        """
        Initialize the analysis workflow.
        
        Args:
            llm_orchestrator: LLM orchestrator for AI analysis
            jurisdiction_detector: Jurisdiction detection service
            indian_processor: Indian legal system processor
            us_processor: US legal system processor
            comparative_analyzer: Cross-border analysis service
        """
        self.llm_orchestrator = llm_orchestrator
        self.jurisdiction_detector = jurisdiction_detector or JurisdictionDetector()
        self.indian_processor = indian_processor or IndianLegalProcessor()
        self.us_processor = us_processor or USLegalProcessor()
        self.comparative_analyzer = comparative_analyzer or ComparativeJurisdictionAnalyzer()
    
    async def analyze_document(
        self,
        document_content: str,
        document_type: str,
        workflow_type: AnalysisWorkflowType = AnalysisWorkflowType.FULL_ANALYSIS,
        user_jurisdiction_hint: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive jurisdiction-aware document analysis.
        
        Args:
            document_content: The document text to analyze
            document_type: Type of document (contract, agreement, etc.)
            workflow_type: Type of analysis workflow to execute
            user_jurisdiction_hint: User-provided jurisdiction hint
            additional_context: Additional context for analysis
            
        Returns:
            Comprehensive analysis results with jurisdiction-specific insights
        """
        try:
            start_time = datetime.utcnow()
            
            # Step 1: Detect jurisdiction
            jurisdiction_analysis = await self._detect_jurisdiction(
                document_content, user_jurisdiction_hint
            )
            
            detected_jurisdiction = JurisdictionType(jurisdiction_analysis["primary_jurisdiction"])
            
            # Step 2: Execute workflow based on type
            if workflow_type == AnalysisWorkflowType.FULL_ANALYSIS:
                analysis_results = await self._execute_full_analysis(
                    document_content, document_type, detected_jurisdiction, 
                    jurisdiction_analysis, additional_context
                )
            else:
                analysis_results = await self._execute_specific_analysis(
                    document_content, document_type, detected_jurisdiction,
                    workflow_type, additional_context
                )
            
            # Step 3: Add jurisdiction-specific processing
            jurisdiction_specific_results = await self._add_jurisdiction_processing(
                document_content, document_type, jurisdiction_analysis, additional_context
            )
            
            # Step 4: Combine results
            final_results = {
                "document_analysis": analysis_results,
                "jurisdiction_analysis": jurisdiction_analysis,
                "jurisdiction_specific": jurisdiction_specific_results,
                "metadata": {
                    "workflow_type": workflow_type.value,
                    "document_type": document_type,
                    "processing_time_seconds": (datetime.utcnow() - start_time).total_seconds(),
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "1.0"
                }
            }
            
            return final_results
            
        except Exception as e:
            logger.error(f"Document analysis workflow failed: {str(e)}")
            raise AIProcessingError(f"Analysis workflow failed: {str(e)}")
    
    async def _detect_jurisdiction(
        self, 
        document_content: str, 
        user_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Detect document jurisdiction with confidence scoring."""
        try:
            # Use jurisdiction detector
            detection_result = self.jurisdiction_detector.detect_jurisdiction(document_content)
            
            # Enhance with AI analysis if confidence is low
            if detection_result.confidence < 0.7:
                ai_jurisdiction_analysis = await self.llm_orchestrator.analyze_document(
                    document_content=document_content[:2000],  # First 2000 chars for jurisdiction
                    document_type="unknown",
                    jurisdiction=JurisdictionType.UNKNOWN,
                    analysis_type="jurisdiction_detection",
                    context={"user_hint": user_hint}
                )
                
                # Combine rule-based and AI results
                detection_result = self._combine_jurisdiction_results(
                    detection_result, ai_jurisdiction_analysis, user_hint
                )
            
            return {
                "primary_jurisdiction": detection_result.jurisdiction,
                "confidence": detection_result.confidence,
                "scores": detection_result.scores,
                "detected_elements": detection_result.detected_elements,
                "us_state": getattr(detection_result, 'us_state', None),
                "user_hint": user_hint,
                "detection_method": "hybrid" if detection_result.confidence < 0.7 else "rule_based"
            }
            
        except Exception as e:
            logger.error(f"Jurisdiction detection failed: {str(e)}")
            # Fallback to unknown jurisdiction
            return {
                "primary_jurisdiction": "unknown",
                "confidence": 0.0,
                "scores": {},
                "detected_elements": [],
                "error": str(e)
            }
    
    async def _execute_full_analysis(
        self,
        document_content: str,
        document_type: str,
        jurisdiction: JurisdictionType,
        jurisdiction_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute comprehensive analysis workflow."""
        
        # Run multiple analysis types in parallel
        analysis_tasks = [
            self.llm_orchestrator.analyze_document(
                document_content, document_type, jurisdiction, 
                "executive_summary", context
            ),
            self.llm_orchestrator.analyze_document(
                document_content, document_type, jurisdiction, 
                "risk_analysis", context
            ),
            self.llm_orchestrator.analyze_document(
                document_content, document_type, jurisdiction, 
                "obligation_extraction", context
            ),
            self.llm_orchestrator.analyze_document(
                document_content, document_type, jurisdiction, 
                "complexity_scoring", context
            )
        ]
        
        # Execute analyses concurrently
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # Process results
        analysis_results = {}
        analysis_types = ["executive_summary", "risk_analysis", "obligation_extraction", "complexity_scoring"]
        
        for i, result in enumerate(results):
            analysis_type = analysis_types[i]
            if isinstance(result, Exception):
                logger.error(f"{analysis_type} failed: {str(result)}")
                analysis_results[analysis_type] = {
                    "error": str(result),
                    "status": "failed"
                }
            else:
                analysis_results[analysis_type] = result
        
        return analysis_results
    
    async def _execute_specific_analysis(
        self,
        document_content: str,
        document_type: str,
        jurisdiction: JurisdictionType,
        workflow_type: AnalysisWorkflowType,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute specific analysis workflow."""
        
        analysis_type = workflow_type.value
        
        result = await self.llm_orchestrator.analyze_document(
            document_content, document_type, jurisdiction, analysis_type, context
        )
        
        return {analysis_type: result}
    
    async def _add_jurisdiction_processing(
        self,
        document_content: str,
        document_type: str,
        jurisdiction_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Add jurisdiction-specific legal processing."""
        
        jurisdiction = jurisdiction_analysis["primary_jurisdiction"]
        jurisdiction_results = {}
        
        try:
            if jurisdiction == "india":
                jurisdiction_results["indian_analysis"] = await self._process_indian_jurisdiction(
                    document_content, document_type, jurisdiction_analysis, context
                )
            elif jurisdiction == "usa":
                jurisdiction_results["us_analysis"] = await self._process_us_jurisdiction(
                    document_content, document_type, jurisdiction_analysis, context
                )
            elif jurisdiction == "cross_border":
                jurisdiction_results["comparative_analysis"] = await self._process_cross_border(
                    document_content, document_type, jurisdiction_analysis, context
                )
            
            return jurisdiction_results
            
        except Exception as e:
            logger.error(f"Jurisdiction-specific processing failed: {str(e)}")
            return {"error": str(e), "jurisdiction": jurisdiction}
    
    async def _process_indian_jurisdiction(
        self,
        document_content: str,
        document_type: str,
        jurisdiction_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process document with Indian legal framework."""
        
        results = {}
        
        # Indian Contract Act analysis
        contract_analysis = self.indian_processor.analyze_contract_act_compliance(document_content)
        results["contract_act_analysis"] = contract_analysis
        
        # Stamp duty calculation
        if document_type in ["agreement", "contract", "mou"]:
            stamp_duty = self.indian_processor.calculate_stamp_duty(
                document_content, document_type, context.get("state", "maharashtra") if context else "maharashtra"
            )
            results["stamp_duty_analysis"] = stamp_duty
        
        # GST implications
        gst_analysis = self.indian_processor.analyze_gst_implications(document_content)
        results["gst_analysis"] = gst_analysis
        
        # AI-enhanced Indian analysis
        ai_indian_analysis = await self.llm_orchestrator.analyze_jurisdiction_specific(
            document_content,
            JurisdictionType.INDIA,
            "indian_comprehensive_analysis",
            document_type=document_type,
            state=context.get("state", "maharashtra") if context else "maharashtra"
        )
        results["ai_enhanced_analysis"] = ai_indian_analysis
        
        return results
    
    async def _process_us_jurisdiction(
        self,
        document_content: str,
        document_type: str,
        jurisdiction_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process document with US legal framework."""
        
        results = {}
        
        # UCC analysis
        ucc_analysis = self.us_processor.analyze_ucc_applicability(document_content)
        results["ucc_analysis"] = ucc_analysis
        
        # Securities law compliance
        securities_analysis = self.us_processor.check_securities_compliance(document_content)
        results["securities_analysis"] = securities_analysis
        
        # Privacy law compliance
        privacy_analysis = self.us_processor.analyze_privacy_compliance(document_content)
        results["privacy_analysis"] = privacy_analysis
        
        # State-specific analysis
        us_state = jurisdiction_analysis.get("us_state", "delaware")
        state_analysis = self.us_processor.analyze_state_law_implications(document_content, us_state)
        results["state_analysis"] = state_analysis
        
        # AI-enhanced US analysis
        ai_us_analysis = await self.llm_orchestrator.analyze_jurisdiction_specific(
            document_content,
            JurisdictionType.USA,
            "us_comprehensive_analysis",
            document_type=document_type,
            state=us_state
        )
        results["ai_enhanced_analysis"] = ai_us_analysis
        
        return results
    
    async def _process_cross_border(
        self,
        document_content: str,
        document_type: str,
        jurisdiction_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process cross-border document analysis."""
        
        results = {}
        
        # Comparative analysis
        comparative_analysis = self.comparative_analyzer.analyze_cross_border_enforceability(
            document_content
        )
        results["enforceability_comparison"] = comparative_analysis
        
        # Tax implications
        tax_analysis = self.comparative_analyzer.analyze_tax_implications(document_content)
        results["tax_implications"] = tax_analysis
        
        # Formalities comparison
        formalities = self.comparative_analyzer.compare_formalities(document_content)
        results["formalities_comparison"] = formalities
        
        # AI-enhanced cross-border analysis
        ai_comparative_analysis = await self.llm_orchestrator.analyze_jurisdiction_specific(
            document_content,
            JurisdictionType.CROSS_BORDER,
            "cross_border_comprehensive_analysis",
            document_type=document_type
        )
        results["ai_enhanced_analysis"] = ai_comparative_analysis
        
        return results
    
    def _combine_jurisdiction_results(
        self,
        rule_based_result,
        ai_result: Dict[str, Any],
        user_hint: Optional[str]
    ):
        """Combine rule-based and AI jurisdiction detection results."""
        
        # This is a simplified combination logic
        # In practice, you'd want more sophisticated weighting
        
        if user_hint:
            # Give higher weight to user hint
            if user_hint.lower() in ["india", "indian"]:
                rule_based_result.jurisdiction = "india"
                rule_based_result.confidence = max(0.8, rule_based_result.confidence)
            elif user_hint.lower() in ["usa", "us", "united states"]:
                rule_based_result.jurisdiction = "usa"
                rule_based_result.confidence = max(0.8, rule_based_result.confidence)
        
        # Enhance with AI insights if available
        if "jurisdiction" in str(ai_result).lower():
            # Extract jurisdiction insights from AI analysis
            # This would need more sophisticated parsing in practice
            pass
        
        return rule_based_result
    
    async def generate_executive_summary_with_jurisdiction_context(
        self,
        document_content: str,
        document_type: str,
        jurisdiction_analysis: Dict[str, Any],
        full_analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary with jurisdiction-specific context."""
        
        jurisdiction = JurisdictionType(jurisdiction_analysis["primary_jurisdiction"])
        
        # Prepare context from full analysis
        context = {
            "jurisdiction_analysis": jurisdiction_analysis,
            "risk_summary": full_analysis_results.get("risk_analysis", {}),
            "obligations_summary": full_analysis_results.get("obligation_extraction", {}),
            "complexity_score": full_analysis_results.get("complexity_scoring", {}),
            "jurisdiction_specific": full_analysis_results.get("jurisdiction_specific", {})
        }
        
        summary = await self.llm_orchestrator.analyze_document(
            document_content=document_content,
            document_type=document_type,
            jurisdiction=jurisdiction,
            analysis_type="executive_summary_with_context",
            context=context
        )
        
        return summary
    
    async def identify_jurisdiction_specific_risks(
        self,
        document_content: str,
        document_type: str,
        jurisdiction: JurisdictionType,
        jurisdiction_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify risks specific to the detected jurisdiction."""
        
        risks = []
        
        if jurisdiction == JurisdictionType.INDIA:
            # Indian-specific risks
            indian_risks = await self.llm_orchestrator.analyze_jurisdiction_specific(
                document_content,
                jurisdiction,
                "indian_risk_analysis",
                document_type=document_type
            )
            risks.extend(indian_risks.get("risks", []))
            
        elif jurisdiction == JurisdictionType.USA:
            # US-specific risks
            us_risks = await self.llm_orchestrator.analyze_jurisdiction_specific(
                document_content,
                jurisdiction,
                "us_risk_analysis",
                document_type=document_type,
                state=jurisdiction_analysis.get("us_state", "delaware")
            )
            risks.extend(us_risks.get("risks", []))
            
        elif jurisdiction == JurisdictionType.CROSS_BORDER:
            # Cross-border risks
            cross_border_risks = await self.llm_orchestrator.analyze_jurisdiction_specific(
                document_content,
                jurisdiction,
                "cross_border_risk_analysis",
                document_type=document_type
            )
            risks.extend(cross_border_risks.get("risks", []))
        
        return risks
    
    async def extract_jurisdiction_specific_obligations(
        self,
        document_content: str,
        document_type: str,
        jurisdiction: JurisdictionType,
        jurisdiction_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract obligations with jurisdiction-specific enforcement context."""
        
        # Base obligation extraction
        base_obligations = await self.llm_orchestrator.analyze_document(
            document_content, document_type, jurisdiction, "obligation_extraction"
        )
        
        # Add jurisdiction-specific enforcement context
        enhanced_obligations = []
        
        for obligation in base_obligations.get("obligations", []):
            enhanced_obligation = obligation.copy()
            
            # Add jurisdiction-specific enforcement mechanisms
            if jurisdiction == JurisdictionType.INDIA:
                enhanced_obligation["indian_enforcement"] = self._get_indian_enforcement_context(obligation)
            elif jurisdiction == JurisdictionType.USA:
                enhanced_obligation["us_enforcement"] = self._get_us_enforcement_context(
                    obligation, jurisdiction_analysis.get("us_state", "delaware")
                )
            
            enhanced_obligations.append(enhanced_obligation)
        
        return enhanced_obligations
    
    def _get_indian_enforcement_context(self, obligation: Dict[str, Any]) -> Dict[str, Any]:
        """Get Indian legal enforcement context for an obligation."""
        return {
            "applicable_acts": ["Indian Contract Act 1872"],
            "enforcement_mechanism": "Civil courts",
            "limitation_period": "3 years from breach",
            "remedies": ["Damages", "Specific performance", "Injunction"]
        }
    
    def _get_us_enforcement_context(self, obligation: Dict[str, Any], state: str) -> Dict[str, Any]:
        """Get US legal enforcement context for an obligation."""
        return {
            "applicable_law": f"{state.title()} state law and federal law",
            "enforcement_mechanism": "State and federal courts",
            "limitation_period": "Varies by state and claim type",
            "remedies": ["Damages", "Specific performance", "Injunction", "Restitution"]
        }