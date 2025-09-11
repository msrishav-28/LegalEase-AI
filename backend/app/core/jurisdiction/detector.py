"""
Jurisdiction detection engine for legal documents.

Provides automatic detection of Indian and US legal documents with confidence scoring,
pattern matching for legal acts, terminology, and court references.
"""

import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class Jurisdiction(Enum):
    """Enumeration of supported jurisdictions."""
    INDIA = "IN"
    USA = "US"
    CROSS_BORDER = "CROSS_BORDER"
    UNKNOWN = "UNKNOWN"


@dataclass
class JurisdictionResult:
    """Result of jurisdiction detection analysis."""
    jurisdiction: Jurisdiction
    confidence: float
    scores: Dict[str, float]
    detected_elements: List[str]
    us_state: Optional[str] = None
    indian_state: Optional[str] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class JurisdictionDetector:
    """
    Jurisdiction detection engine with Indian and US legal indicators.
    
    Implements scoring algorithm for jurisdiction confidence and pattern matching
    for legal acts, terminology, and court references with state-level detection.
    """
    
    def __init__(self):
        """Initialize JurisdictionDetector with legal patterns and indicators."""
        self._initialize_indian_patterns()
        self._initialize_us_patterns()
        self._initialize_court_patterns()
        self._initialize_currency_patterns()
        self._initialize_legal_terminology()
        
    def _initialize_indian_patterns(self):
        """Initialize Indian legal system patterns and indicators."""
        
        # Indian Acts and Legislation
        self.indian_acts = {
            'Indian Contract Act': ['indian contract act', 'contract act 1872', 'contract act, 1872'],
            'Companies Act': ['companies act 2013', 'companies act, 2013', 'companies act 1956'],
            'GST Act': ['gst act', 'goods and services tax', 'cgst', 'sgst', 'igst'],
            'Income Tax Act': ['income tax act', 'income tax act 1961'],
            'Arbitration Act': ['arbitration and conciliation act', 'arbitration act 2015'],
            'SEBI Act': ['sebi act', 'securities and exchange board'],
            'RBI Act': ['rbi act', 'reserve bank of india act'],
            'FEMA': ['fema', 'foreign exchange management act'],
            'Consumer Protection Act': ['consumer protection act'],
            'Indian Penal Code': ['indian penal code', 'ipc'],
            'Code of Civil Procedure': ['code of civil procedure', 'cpc'],
            'Evidence Act': ['indian evidence act', 'evidence act 1872']
        }
        
        # Indian States for jurisdiction detection
        self.indian_states = {
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
            'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
            'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
            'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
            'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Puducherry', 'Chandigarh',
            'Andaman and Nicobar Islands', 'Dadra and Nagar Haveli', 'Daman and Diu',
            'Lakshadweep'
        }
        
        # Indian legal terminology
        self.indian_legal_terms = {
            'stamp duty', 'registration', 'registrar', 'sub-registrar', 'notarization',
            'advocate', 'senior advocate', 'barrister', 'solicitor general',
            'attorney general of india', 'public prosecutor', 'additional solicitor general',
            'crore', 'lakh', 'rupees', 'inr', 'paisa',
            'supreme court of india', 'sessions court',
            'magistrate', 'chief justice of india', 'cji',
            'indian constitution', 'fundamental rights', 'directive principles',
            'writ petition', 'mandamus', 'certiorari', 'prohibition', 'quo warranto',
            'habeas corpus', 'public interest litigation', 'pil',
            'indian kanoon', 'bare act', 'all india reporter', 'air',
            'supreme court cases', 'scc', 'indian law reports', 'ilr'
        }
        
        # Indian business and legal entities
        self.indian_entities = {
            'private limited', 'pvt ltd', 'public limited',
            'partnership firm', 'sole proprietorship', 'hindu undivided family', 'huf',
            'section 8 company', 'producer company', 'nidhi company',
            'cooperative society', 'trust', 'society'
        }
        
        # Indian regulatory bodies
        self.indian_regulators = {
            'sebi', 'rbi', 'irdai', 'trai', 'cci', 'nclt', 'nclat',
            'securities and exchange board of india',
            'reserve bank of india', 'insurance regulatory',
            'telecom regulatory authority', 'competition commission',
            'national company law tribunal', 'national company law appellate tribunal'
        }
    
    def _initialize_us_patterns(self):
        """Initialize US legal system patterns and indicators."""
        
        # US Federal Laws and Codes
        self.us_federal_codes = {
            'USC': ['u.s.c.', 'usc', 'united states code'],
            'CFR': ['c.f.r.', 'cfr', 'code of federal regulations'],
            'UCC': ['uniform commercial code', 'ucc'],
            'Securities Act': ['securities act of 1933', 'securities act 1933'],
            'Exchange Act': ['securities exchange act', 'exchange act of 1934'],
            'Sarbanes-Oxley': ['sarbanes-oxley', 'sox', 'sarbox'],
            'Dodd-Frank': ['dodd-frank', 'dodd frank act'],
            'CCPA': ['california consumer privacy act', 'ccpa'],
            'GDPR': ['general data protection regulation', 'gdpr'],
            'HIPAA': ['health insurance portability', 'hipaa'],
            'ADA': ['americans with disabilities act', 'ada'],
            'FLSA': ['fair labor standards act', 'flsa'],
            'NLRA': ['national labor relations act', 'nlra']
        }
        
        # US States
        self.us_states = {
            'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
            'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
            'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
            'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
            'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
            'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
            'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
            'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
            'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
            'West Virginia', 'Wisconsin', 'Wyoming', 'District of Columbia'
        }
        
        # US legal terminology
        self.us_legal_terms = {
            'attorney', 'counsel', 'esquire', 'esq', 'law firm', 'legal counsel',
            'district attorney', 'prosecutor', 'public defender',
            'federal judge', 'magistrate judge', 'chief justice',
            'constitution', 'bill of rights', 'amendment', 'constitutional',
            'federal register', 'federal law', 'state law', 'common law',
            'case law', 'precedent', 'stare decisis',
            'venue', 'forum', 'choice of law', 'conflict of laws',
            'class action', 'summary judgment', 'motion to dismiss',
            'discovery', 'deposition', 'interrogatories', 'subpoena'
        }
        
        # US business entities
        self.us_entities = {
            'corporation', 'corp', 'inc', 'incorporated', 'company', 'co',
            'limited liability company', 'llc', 'limited partnership', 'lp',
            'professional corporation', 'pc',
            'professional limited liability company', 'pllc',
            'partnership', 'joint venture',
            'delaware corporation', 'c-corp', 's-corp', 'b-corp'
        }
        
        # US regulatory bodies
        self.us_regulators = {
            'sec', 'securities and exchange commission', 'cftc',
            'commodity futures trading commission', 'finra',
            'financial industry regulatory authority', 'fdic',
            'federal deposit insurance corporation', 'occ',
            'office of the comptroller', 'federal reserve', 'fed',
            'ftc', 'federal trade commission', 'doj', 'department of justice',
            'irs', 'internal revenue service', 'treasury department'
        }
    
    def _initialize_court_patterns(self):
        """Initialize court system patterns for both jurisdictions."""
        
        # Indian Courts (more specific patterns)
        self.indian_courts = {
            'supreme court of india', 'high court of', 'bombay high court',
            'delhi high court', 'madras high court', 'calcutta high court',
            'sessions court', 'magistrate court', 'family court',
            'consumer court', 'labour court', 'industrial tribunal',
            'debt recovery tribunal', 'drt', 'appellate tribunal',
            'income tax appellate tribunal', 'itat',
            'customs excise and service tax appellate tribunal', 'cestat',
            'national green tribunal', 'ngt',
            'armed forces tribunal', 'aft'
        }
        
        # US Courts (more specific patterns)
        self.us_courts = {
            'federal court', 'federal district court', 'circuit court',
            'court of appeals', 'appellate court', 'bankruptcy court', 'tax court',
            'state supreme court', 'superior court', 'municipal court', 
            'justice court', 'probate court', 'small claims court'
        }
    
    def _initialize_currency_patterns(self):
        """Initialize currency and monetary patterns."""
        
        # Indian currency patterns
        self.indian_currency_patterns = [
            r'\b(?:rs\.?|rupees?|inr)\s*[\d,]+(?:\.\d{2})?\b',
            r'\b[\d,]+\s*(?:rs\.?|rupees?|inr)\b',
            r'\b(?:\d+\s*)?(?:crores?|lakhs?)\b',
            r'₹\s*[\d,]+(?:\.\d{2})?'
        ]
        
        # US currency patterns
        self.us_currency_patterns = [
            r'\$\s*[\d,]+(?:\.\d{2})?',
            r'\b(?:usd|dollars?)\s*[\d,]+(?:\.\d{2})?\b',
            r'\b[\d,]+\s*(?:usd|dollars?)\b',
            r'\b(?:million|billion|trillion)\s*dollars?\b'
        ]
    
    def _initialize_legal_terminology(self):
        """Initialize jurisdiction-specific legal terminology."""
        
        # Terms more common in Indian legal documents
        self.indian_specific_terms = {
            'whereas', 'witnesseth', 'know all men by these presents',
            'in witness whereof', 'hereunto set', 'common seal',
            'executed at', 'in the presence of witnesses',
            'stamp paper', 'non-judicial stamp paper', 'judicial stamp paper',
            'franking', 'e-stamping', 'adjudication',
            'indian majority act', 'indian succession act',
            'transfer of property act', 'specific relief act',
            'limitation act', 'registration act', 'stamp act',
            'maharashtra stamp act', 'karnataka stamp act', 'delhi stamp act'
        }
        
        # Terms more common in US legal documents
        self.us_specific_terms = {
            'whereas', 'now therefore', 'in witness whereof',
            'executed as of', 'effective date', 'governing law',
            'choice of law', 'forum selection', 'arbitration clause',
            'class action waiver', 'jury trial waiver',
            'attorney fees', 'prevailing party', 'liquidated damages',
            'specific performance', 'injunctive relief',
            'delaware law', 'new york law', 'california law',
            'laws of the state', 'state law', 'corporate law',
            'governed by and construed', 'conflict of laws'
        }
    
    def detect_jurisdiction(self, text: str) -> JurisdictionResult:
        """
        Detect jurisdiction of a legal document with confidence scoring.
        
        Args:
            text: Document text content
            
        Returns:
            JurisdictionResult with detected jurisdiction and confidence
        """
        if not text or not text.strip():
            return JurisdictionResult(
                jurisdiction=Jurisdiction.UNKNOWN,
                confidence=0.0,
                scores={},
                detected_elements=[]
            )
        
        text_lower = text.lower()
        
        # Calculate scores for each jurisdiction
        indian_score, indian_elements = self._calculate_indian_score(text_lower, text)
        us_score, us_elements = self._calculate_us_score(text_lower, text)
        
        # Detect specific states
        indian_state = self._detect_indian_state(text)
        us_state = self._detect_us_state(text)
        
        # Determine primary jurisdiction
        jurisdiction, confidence = self._determine_jurisdiction(indian_score, us_score)
        
        # Collect all detected elements
        all_elements = indian_elements + us_elements
        
        # Create scores dictionary
        scores = {
            'india': indian_score,
            'usa': us_score,
            'total_elements': len(all_elements)
        }
        
        # Additional metadata
        metadata = {
            'text_length': len(text),
            'indian_elements_count': len(indian_elements),
            'us_elements_count': len(us_elements),
            'has_currency_indicators': self._has_currency_indicators(text_lower),
            'has_court_references': self._has_court_references(text_lower)
        }
        
        return JurisdictionResult(
            jurisdiction=jurisdiction,
            confidence=confidence,
            scores=scores,
            detected_elements=all_elements,
            us_state=us_state,
            indian_state=indian_state,
            metadata=metadata
        )
    
    def _calculate_indian_score(self, text_lower: str, original_text: str) -> Tuple[float, List[str]]:
        """Calculate Indian jurisdiction score and detected elements."""
        score = 0.0
        elements = []
        
        # Check Indian Acts (high weight)
        for act_name, patterns in self.indian_acts.items():
            for pattern in patterns:
                if pattern in text_lower:
                    score += 3.0
                    elements.append(f"Indian Act: {act_name}")
        
        # Check Indian legal terms (medium weight)
        for term in self.indian_legal_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                score += 1.5
                elements.append(f"Indian Term: {term}")
        
        # Check Indian courts (high weight)
        for court in self.indian_courts:
            if court in text_lower:
                score += 2.5
                elements.append(f"Indian Court: {court}")
        
        # Check Indian entities (medium weight)
        for entity in self.indian_entities:
            if re.search(r'\b' + re.escape(entity) + r'\b', text_lower):
                score += 1.0
                elements.append(f"Indian Entity: {entity}")
        
        # Check Indian regulators (high weight)
        for regulator in self.indian_regulators:
            if re.search(r'\b' + re.escape(regulator) + r'\b', text_lower):
                score += 2.0
                elements.append(f"Indian Regulator: {regulator}")
        
        # Check Indian currency patterns (medium weight)
        for pattern in self.indian_currency_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                score += len(matches) * 1.5
                elements.extend([f"Indian Currency: {match}" for match in matches[:3]])
        
        # Check Indian-specific terms (low weight)
        for term in self.indian_specific_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                score += 0.5
                elements.append(f"Indian Specific: {term}")
        
        # Check for Indian states (medium weight)
        for state in self.indian_states:
            if state.lower() in text_lower:
                score += 1.0
                elements.append(f"Indian State: {state}")
        
        return score, elements[:20]  # Limit elements for readability
    
    def _calculate_us_score(self, text_lower: str, original_text: str) -> Tuple[float, List[str]]:
        """Calculate US jurisdiction score and detected elements."""
        score = 0.0
        elements = []
        
        # Check US Federal Codes (high weight)
        for code_name, patterns in self.us_federal_codes.items():
            for pattern in patterns:
                if pattern in text_lower:
                    score += 3.0
                    elements.append(f"US Code: {code_name}")
        
        # Check US legal terms (medium weight)
        for term in self.us_legal_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                score += 1.5
                elements.append(f"US Term: {term}")
        
        # Check US courts (high weight)
        for court in self.us_courts:
            if court in text_lower:
                score += 2.5
                elements.append(f"US Court: {court}")
        
        # Check US entities (medium weight)
        for entity in self.us_entities:
            if re.search(r'\b' + re.escape(entity) + r'\b', text_lower):
                score += 1.0
                elements.append(f"US Entity: {entity}")
        
        # Check US regulators (high weight)
        for regulator in self.us_regulators:
            if re.search(r'\b' + re.escape(regulator) + r'\b', text_lower):
                score += 2.0
                elements.append(f"US Regulator: {regulator}")
        
        # Check US currency patterns (medium weight)
        for pattern in self.us_currency_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                score += len(matches) * 1.5
                elements.extend([f"US Currency: {match}" for match in matches[:3]])
        
        # Check US-specific terms (variable weight)
        for term in self.us_specific_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                # Higher weight for governing law terms
                if 'law' in term or 'govern' in term:
                    score += 1.5
                else:
                    score += 0.5
                elements.append(f"US Specific: {term}")
        
        # Check for US states (medium weight)
        for state in self.us_states:
            if state.lower() in text_lower:
                score += 1.0
                elements.append(f"US State: {state}")
        
        return score, elements[:20]  # Limit elements for readability
    
    def _detect_indian_state(self, text: str) -> Optional[str]:
        """Detect specific Indian state mentioned in the document."""
        text_lower = text.lower()
        
        for state in self.indian_states:
            if state.lower() in text_lower:
                return state
        
        return None
    
    def _detect_us_state(self, text: str) -> Optional[str]:
        """Detect specific US state mentioned in the document."""
        text_lower = text.lower()
        
        # First check for governing law references (highest priority)
        state_law_patterns = [
            r'(?:laws?\s+of\s+(?:the\s+state\s+of\s+)?|governed\s+by\s+(?:the\s+laws?\s+of\s+)?(?:the\s+state\s+of\s+)?)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'under\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:corporate\s+)?law',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:corporate\s+)?law\s+(?:shall\s+)?govern'
        ]
        
        for pattern in state_law_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                potential_state = match.group(1).strip()
                if potential_state in self.us_states:
                    return potential_state
        
        # Then check for explicit state mentions
        for state in self.us_states:
            if state.lower() in text_lower:
                return state
        
        return None
    
    def _determine_jurisdiction(self, indian_score: float, us_score: float) -> Tuple[Jurisdiction, float]:
        """Determine primary jurisdiction and confidence based on scores."""
        
        # If both scores are very low, return unknown
        if indian_score < 1.0 and us_score < 1.0:
            return Jurisdiction.UNKNOWN, 0.0
        
        # Determine primary jurisdiction
        if indian_score > us_score:
            jurisdiction = Jurisdiction.INDIA
            primary_score = indian_score
            secondary_score = us_score
        else:
            jurisdiction = Jurisdiction.USA
            primary_score = us_score
            secondary_score = indian_score
        
        # Check for cross-border only if both scores are high AND close to each other
        score_difference = abs(indian_score - us_score)
        min_score = min(indian_score, us_score)
        
        # More restrictive cross-border detection - need both scores high and close
        if (indian_score >= 5.0 and us_score >= 5.0 and 
            score_difference <= 5.0 and min_score >= 4.0):
            total_score = indian_score + us_score
            confidence = min(0.9, total_score / 25.0)  # Cap at 0.9 for cross-border
            return Jurisdiction.CROSS_BORDER, confidence
        
        # Calculate confidence based on score difference and absolute score
        score_ratio = primary_score / (secondary_score + 1.0)  # Add 1 to avoid division by zero
        absolute_confidence = min(1.0, primary_score / 10.0)  # Normalize to 0-1, lower threshold
        
        # Combine ratio and absolute confidence with better weighting
        confidence = min(0.95, (absolute_confidence * 0.8) + (min(1.0, score_ratio / 2.5) * 0.2))
        
        return jurisdiction, confidence
    
    def _has_currency_indicators(self, text_lower: str) -> bool:
        """Check if document has currency indicators."""
        for pattern in self.indian_currency_patterns + self.us_currency_patterns:
            if re.search(pattern, text_lower):
                return True
        return False
    
    def _has_court_references(self, text_lower: str) -> bool:
        """Check if document has court references."""
        all_courts = self.indian_courts | self.us_courts
        for court in all_courts:
            if court in text_lower:
                return True
        return False
    
    def get_jurisdiction_summary(self, result: JurisdictionResult) -> Dict:
        """
        Get a human-readable summary of jurisdiction detection results.
        
        Args:
            result: JurisdictionResult from detect_jurisdiction
            
        Returns:
            Dictionary with summary information
        """
        summary = {
            'jurisdiction': result.jurisdiction.value,
            'confidence_percentage': round(result.confidence * 100, 1),
            'confidence_level': self._get_confidence_level(result.confidence),
            'primary_indicators': result.detected_elements[:5],
            'total_indicators': len(result.detected_elements)
        }
        
        if result.us_state:
            summary['us_state'] = result.us_state
        
        if result.indian_state:
            summary['indian_state'] = result.indian_state
        
        if result.jurisdiction == Jurisdiction.CROSS_BORDER:
            summary['note'] = 'Document contains significant indicators from both Indian and US legal systems'
        
        return summary
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence score to human-readable level."""
        if confidence >= 0.8:
            return 'High'
        elif confidence >= 0.6:
            return 'Medium'
        elif confidence >= 0.3:
            return 'Low'
        else:
            return 'Very Low'