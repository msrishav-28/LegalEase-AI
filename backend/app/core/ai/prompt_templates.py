"""Jurisdiction-aware prompt templates for legal document analysis."""

from typing import Dict, Any, Optional
from enum import Enum


class JurisdictionType(str, Enum):
    """Supported jurisdiction types."""
    INDIA = "india"
    USA = "usa"
    CROSS_BORDER = "cross_border"
    UNKNOWN = "unknown"


class PromptTemplateManager:
    """Manages jurisdiction-specific prompt templates for AI analysis."""
    
    def __init__(self):
        self._templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize all prompt templates organized by jurisdiction and task type."""
        return {
            "system_prompts": {
                "base": """You are LegalEase AI, an expert legal document analysis assistant specializing in Indian and US legal systems. 
You provide accurate, jurisdiction-specific analysis of legal documents with deep understanding of:
- Indian legal framework (Contract Act 1872, Companies Act 2013, GST Act, state-specific laws)
- US legal framework (Federal law, state law, UCC, securities regulations)
- Cross-border legal considerations and comparative analysis

Always provide clear, actionable insights with proper legal citations and confidence levels.""",
                
                "india": """You are analyzing documents under Indian legal jurisdiction. Focus on:
- Indian Contract Act 1872 compliance and applicability
- Companies Act 2013 requirements for corporate documents
- GST implications and tax considerations
- State-specific stamp duty and registration requirements
- Indian court precedents and legal terminology
- Regulatory compliance (SEBI, RBI, FEMA where applicable)

Provide analysis in the context of Indian legal practice and cite relevant sections of Indian Acts.""",
                
                "usa": """You are analyzing documents under US legal jurisdiction. Focus on:
- Federal law applicability and compliance
- State law variations and choice of law considerations
- Uniform Commercial Code (UCC) applicability
- Securities law compliance (SEC regulations)
- Privacy law compliance (CCPA, state privacy laws)
- Contract enforceability under US legal principles

Provide analysis considering both federal and state law implications.""",
                
                "cross_border": """You are analyzing cross-border documents involving Indian and US jurisdictions. Focus on:
- Enforceability comparison between Indian and US legal systems
- Governing law and jurisdiction clause analysis
- Tax treaty implications (India-US DTAA)
- Foreign exchange regulations (FEMA in India, US regulations)
- Dispute resolution mechanisms suitable for cross-border transactions
- Compliance requirements in both jurisdictions

Provide comparative analysis highlighting key differences and recommendations."""
            },
            
            "analysis_prompts": {
                "executive_summary": """Analyze the following legal document and provide a comprehensive executive summary.

Document Content: {document_content}
Jurisdiction: {jurisdiction}
Document Type: {document_type}

Provide a structured summary including:
1. Document Overview (parties, purpose, key terms)
2. Jurisdiction-specific Legal Framework
3. Key Obligations and Rights
4. Risk Assessment
5. Compliance Requirements
6. Recommendations

Format your response as structured JSON with clear sections.""",
                
                "risk_analysis": """Perform a detailed risk analysis of the following legal document.

Document Content: {document_content}
Jurisdiction: {jurisdiction}
Analysis Context: {context}

Identify and analyze:
1. Legal Risks (enforceability, compliance, regulatory)
2. Commercial Risks (financial, operational, reputational)
3. Jurisdiction-specific Risks
4. Mitigation Strategies
5. Risk Severity (High/Medium/Low with justification)

Provide specific recommendations for each identified risk.""",
                
                "obligation_extraction": """Extract and analyze all legal obligations from the following document.

Document Content: {document_content}
Jurisdiction: {jurisdiction}

For each obligation, provide:
1. Obligation Description
2. Responsible Party
3. Timeline/Deadline
4. Consequences of Non-compliance
5. Jurisdiction-specific Enforcement Mechanisms
6. Compliance Requirements

Structure the response as a detailed list with clear categorization.""",
                
                "complexity_scoring": """Assess the complexity of the following legal document.

Document Content: {document_content}
Jurisdiction: {jurisdiction}

Evaluate complexity based on:
1. Legal Language Complexity (1-10 scale)
2. Structural Complexity (number of sections, cross-references)
3. Jurisdiction-specific Complexity
4. Commercial Complexity
5. Regulatory Complexity

Provide an overall complexity score (1-10) with detailed justification for each component."""
            },
            
            "jurisdiction_specific": {
                "indian_stamp_duty": """Analyze stamp duty requirements for this document under Indian law.

Document Content: {document_content}
Document Type: {document_type}
State: {state}

Provide:
1. Applicable stamp duty rates
2. State-specific variations
3. Registration requirements
4. Compliance timeline
5. Penalties for non-compliance
6. Exemptions (if any)""",
                
                "indian_gst_analysis": """Analyze GST implications of this document under Indian law.

Document Content: {document_content}
Transaction Type: {transaction_type}

Provide:
1. GST applicability and rates
2. Input tax credit implications
3. Compliance requirements
4. Documentation needed
5. Timeline for compliance
6. Penalties for non-compliance""",
                
                "us_ucc_analysis": """Analyze UCC applicability and compliance for this document.

Document Content: {document_content}
Transaction Type: {transaction_type}
State: {state}

Provide:
1. Applicable UCC articles
2. State-specific UCC variations
3. Compliance requirements
4. Perfection requirements (if applicable)
5. Enforcement mechanisms
6. Recommendations for compliance""",
                
                "cross_border_comparison": """Compare legal requirements between Indian and US jurisdictions for this document.

Document Content: {document_content}
Document Type: {document_type}

Provide comparative analysis:
1. Enforceability comparison
2. Formalities differences (stamp duty, notarization, witnesses)
3. Tax implications in both jurisdictions
4. Regulatory compliance differences
5. Dispute resolution options
6. Recommendations for optimal structure"""
            },
            
            "chat_prompts": {
                "contextual_qa": """Answer the following question about the legal document with jurisdiction-specific context.

Document Content: {document_content}
Jurisdiction: {jurisdiction}
Previous Context: {conversation_history}
Question: {question}

Provide a comprehensive answer that:
1. Directly addresses the question
2. References specific document sections
3. Includes jurisdiction-specific legal context
4. Cites relevant laws/regulations
5. Provides confidence level (High/Medium/Low)
6. Suggests follow-up questions if relevant""",
                
                "clause_explanation": """Explain the following clause in detail with jurisdiction-specific context.

Clause: {clause_text}
Document Context: {document_context}
Jurisdiction: {jurisdiction}

Provide explanation covering:
1. Plain language interpretation
2. Legal implications
3. Jurisdiction-specific considerations
4. Potential risks or benefits
5. Standard market practice
6. Suggested modifications (if any)"""
            }
        }
    
    def get_system_prompt(self, jurisdiction: JurisdictionType) -> str:
        """Get the appropriate system prompt for the jurisdiction."""
        base_prompt = self._templates["system_prompts"]["base"]
        
        if jurisdiction == JurisdictionType.INDIA:
            return f"{base_prompt}\n\n{self._templates['system_prompts']['india']}"
        elif jurisdiction == JurisdictionType.USA:
            return f"{base_prompt}\n\n{self._templates['system_prompts']['usa']}"
        elif jurisdiction == JurisdictionType.CROSS_BORDER:
            return f"{base_prompt}\n\n{self._templates['system_prompts']['cross_border']}"
        else:
            return base_prompt
    
    def get_analysis_prompt(self, analysis_type: str, **kwargs) -> str:
        """Get analysis prompt template with parameters filled in."""
        if analysis_type not in self._templates["analysis_prompts"]:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        template = self._templates["analysis_prompts"][analysis_type]
        return template.format(**kwargs)
    
    def get_jurisdiction_prompt(self, prompt_type: str, **kwargs) -> str:
        """Get jurisdiction-specific prompt template with parameters filled in."""
        if prompt_type not in self._templates["jurisdiction_specific"]:
            raise ValueError(f"Unknown jurisdiction prompt type: {prompt_type}")
        
        template = self._templates["jurisdiction_specific"][prompt_type]
        return template.format(**kwargs)
    
    def get_chat_prompt(self, prompt_type: str, **kwargs) -> str:
        """Get chat prompt template with parameters filled in."""
        if prompt_type not in self._templates["chat_prompts"]:
            raise ValueError(f"Unknown chat prompt type: {prompt_type}")
        
        template = self._templates["chat_prompts"][prompt_type]
        return template.format(**kwargs)
    
    def add_custom_template(self, category: str, name: str, template: str) -> None:
        """Add a custom prompt template."""
        if category not in self._templates:
            self._templates[category] = {}
        self._templates[category][name] = template
    
    def list_available_templates(self) -> Dict[str, list]:
        """List all available template categories and names."""
        return {
            category: list(templates.keys()) 
            for category, templates in self._templates.items()
        }