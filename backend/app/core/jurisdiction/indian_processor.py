"""
Indian legal system processor.

Provides comprehensive analysis of Indian legal documents including acts database integration,
stamp duty calculation, GST analysis, monetary amount extraction, and compliance checking.
"""

import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)


class IndianState(Enum):
    """Indian states and union territories for jurisdiction-specific processing."""
    ANDHRA_PRADESH = "Andhra Pradesh"
    ARUNACHAL_PRADESH = "Arunachal Pradesh"
    ASSAM = "Assam"
    BIHAR = "Bihar"
    CHHATTISGARH = "Chhattisgarh"
    GOA = "Goa"
    GUJARAT = "Gujarat"
    HARYANA = "Haryana"
    HIMACHAL_PRADESH = "Himachal Pradesh"
    JHARKHAND = "Jharkhand"
    KARNATAKA = "Karnataka"
    KERALA = "Kerala"
    MADHYA_PRADESH = "Madhya Pradesh"
    MAHARASHTRA = "Maharashtra"
    MANIPUR = "Manipur"
    MEGHALAYA = "Meghalaya"
    MIZORAM = "Mizoram"
    NAGALAND = "Nagaland"
    ODISHA = "Odisha"
    PUNJAB = "Punjab"
    RAJASTHAN = "Rajasthan"
    SIKKIM = "Sikkim"
    TAMIL_NADU = "Tamil Nadu"
    TELANGANA = "Telangana"
    TRIPURA = "Tripura"
    UTTAR_PRADESH = "Uttar Pradesh"
    UTTARAKHAND = "Uttarakhand"
    WEST_BENGAL = "West Bengal"
    DELHI = "Delhi"
    JAMMU_KASHMIR = "Jammu and Kashmir"
    LADAKH = "Ladakh"
    PUDUCHERRY = "Puducherry"
    CHANDIGARH = "Chandigarh"
    ANDAMAN_NICOBAR = "Andaman and Nicobar Islands"
    DADRA_NAGAR_HAVELI = "Dadra and Nagar Haveli"
    DAMAN_DIU = "Daman and Diu"
    LAKSHADWEEP = "Lakshadweep"


class DocumentType(Enum):
    """Types of legal documents for stamp duty calculation."""
    AGREEMENT = "agreement"
    CONVEYANCE = "conveyance"
    LEASE = "lease"
    MORTGAGE = "mortgage"
    PARTNERSHIP = "partnership"
    POWER_OF_ATTORNEY = "power_of_attorney"
    PROMISSORY_NOTE = "promissory_note"
    SHARE_TRANSFER = "share_transfer"
    LOAN_AGREEMENT = "loan_agreement"
    SERVICE_AGREEMENT = "service_agreement"
    EMPLOYMENT = "employment"
    NDA = "nda"
    OTHER = "other"


@dataclass
class ActReference:
    """Reference to an Indian legal act found in the document."""
    act_name: str
    full_name: str
    year: Optional[int]
    sections: List[str]
    confidence: float
    context: str


@dataclass
class StampDutyAnalysis:
    """Stamp duty calculation and requirements analysis."""
    state: IndianState
    document_type: DocumentType
    consideration_amount: Optional[Decimal]
    stamp_duty_rate: float
    calculated_duty: Optional[Decimal]
    minimum_duty: Decimal
    maximum_duty: Optional[Decimal]
    exemptions: List[str]
    requirements: List[str]
    compliance_status: str


@dataclass
class GSTAnalysis:
    """GST implications and compliance analysis."""
    applicable: bool
    gst_rate: Optional[float]
    hsn_codes: List[str]
    place_of_supply: Optional[str]
    reverse_charge: bool
    exemptions: List[str]
    compliance_requirements: List[str]
    registration_required: bool


@dataclass
class MonetaryAmount:
    """Extracted monetary amount with Indian currency formatting."""
    amount: Decimal
    currency: str
    original_text: str
    formatted_amount: str
    amount_in_words: Optional[str]


@dataclass
class ComplianceCheck:
    """Compliance checking results for Indian legal requirements."""
    compliant: bool
    violations: List[str]
    recommendations: List[str]
    mandatory_clauses: List[str]
    missing_clauses: List[str]
    risk_level: str


@dataclass
class RegistrationRequirement:
    """Registration requirements for different document types."""
    required: bool
    authority: str
    time_limit: str
    fees: Optional[Decimal]
    documents_needed: List[str]
    consequences_of_non_registration: List[str]


@dataclass
class IndianLegalAnalysis:
    """Complete Indian legal analysis results."""
    act_references: List[ActReference]
    stamp_duty: StampDutyAnalysis
    gst_analysis: GSTAnalysis
    monetary_amounts: List[MonetaryAmount]
    compliance_check: ComplianceCheck
    registration_requirements: List[RegistrationRequirement]
    applicable_laws: List[str]
    jurisdiction_specific_notes: List[str]


class IndianLegalProcessor:
    """
    Indian legal system processor with acts database integration.
    
    Provides comprehensive analysis including Indian Contract Act, Companies Act,
    GST Act reference systems, stamp duty calculation, and compliance checking.
    """
    
    def __init__(self):
        """Initialize IndianLegalProcessor with legal databases and patterns."""
        self._initialize_acts_database()
        self._initialize_stamp_duty_rates()
        self._initialize_gst_database()
        self._initialize_monetary_patterns()
        self._initialize_compliance_rules()
        
    def _initialize_acts_database(self):
        """Initialize comprehensive Indian acts database."""
        self.indian_acts = {
            'Indian Contract Act, 1872': {
                'keywords': ['contract act', 'indian contract act', 'contract act 1872', 'contract act, 1872'],
                'key_sections': {
                    '2': 'Interpretation clause',
                    '10': 'What agreements are contracts',
                    '11': 'Who are competent to contract',
                    '13': 'Consideration',
                    '23': 'What consideration and objects are lawful',
                    '56': 'Agreement to do impossible act',
                    '73': 'Compensation for loss or damage caused by breach of contract',
                    '124': 'Contract of indemnity',
                    '148': 'Bailment, bailor and bailee defined'
                },
                'applicability': ['contracts', 'agreements', 'consideration', 'breach', 'damages']
            },
            'Companies Act, 2013': {
                'keywords': ['companies act', 'companies act 2013', 'companies act, 2013'],
                'key_sections': {
                    '2': 'Definitions',
                    '3': 'Formation of company',
                    '149': 'Company to have Board of Directors',
                    '179': 'Powers of Board',
                    '188': 'Related party transactions',
                    '230': 'Power to compromise or make arrangements with creditors and members'
                },
                'applicability': ['incorporation', 'directors', 'shareholders', 'corporate governance']
            },
            'Goods and Services Tax Act, 2017': {
                'keywords': ['gst act', 'goods and services tax', 'cgst', 'sgst', 'igst', 'utgst'],
                'key_sections': {
                    '2': 'Definitions',
                    '7': 'Scope of supply',
                    '9': 'Levy and collection of tax',
                    '12': 'Value of supply',
                    '16': 'Eligibility and conditions for taking input tax credit'
                },
                'applicability': ['supply of goods', 'supply of services', 'tax liability', 'input credit']
            },
            'Income Tax Act, 1961': {
                'keywords': ['income tax act', 'income tax act 1961', 'it act'],
                'key_sections': {
                    '2': 'Definitions',
                    '4': 'Charge of income-tax',
                    '194C': 'Payment to contractors',
                    '194J': 'Payment of fees for professional or technical services'
                },
                'applicability': ['tax deduction', 'tds', 'professional fees', 'contractor payments']
            },
            'Arbitration and Conciliation Act, 2015': {
                'keywords': ['arbitration act', 'arbitration and conciliation act', 'arbitration act 2015'],
                'key_sections': {
                    '7': 'Arbitration agreement',
                    '11': 'Appointment of arbitrators',
                    '31': 'Form and contents of arbitral award',
                    '34': 'Application for setting aside arbitral award'
                },
                'applicability': ['dispute resolution', 'arbitration clause', 'arbitral award']
            },
            'Transfer of Property Act, 1882': {
                'keywords': ['transfer of property act', 'property act 1882', 'tpa'],
                'key_sections': {
                    '5': 'Transfer of property defined',
                    '54': 'Sale defined',
                    '58': 'Mortgage defined',
                    '105': 'Lease defined'
                },
                'applicability': ['property transfer', 'sale', 'mortgage', 'lease']
            },
            'Specific Relief Act, 1963': {
                'keywords': ['specific relief act', 'specific relief act 1963'],
                'key_sections': {
                    '10': 'Specific performance of part of contract',
                    '12': 'When specific performance enforceable',
                    '20': 'Discretion of court as to decreeing specific performance'
                },
                'applicability': ['specific performance', 'injunction', 'declaratory relief']
            },
            'Limitation Act, 1963': {
                'keywords': ['limitation act', 'limitation act 1963'],
                'key_sections': {
                    '3': 'Bar of limitation',
                    '5': 'Extension of prescribed period in certain cases'
                },
                'applicability': ['limitation period', 'time bar', 'prescription']
            }
        }
        
    def _initialize_stamp_duty_rates(self):
        """Initialize stamp duty rates for different states and document types."""
        # Sample rates - in practice, this would be a comprehensive database
        self.stamp_duty_rates = {
            IndianState.MAHARASHTRA: {
                DocumentType.AGREEMENT: {'rate': 0.1, 'minimum': 100, 'maximum': None},
                DocumentType.SERVICE_AGREEMENT: {'rate': 0.1, 'minimum': 100, 'maximum': None},
                DocumentType.CONVEYANCE: {'rate': 5.0, 'minimum': 100, 'maximum': None},
                DocumentType.LEASE: {'rate': 0.25, 'minimum': 100, 'maximum': None},
                DocumentType.MORTGAGE: {'rate': 0.5, 'minimum': 100, 'maximum': None},
                DocumentType.POWER_OF_ATTORNEY: {'rate': 0, 'minimum': 100, 'maximum': None},
                DocumentType.SHARE_TRANSFER: {'rate': 0.25, 'minimum': 100, 'maximum': None}
            },
            IndianState.DELHI: {
                DocumentType.AGREEMENT: {'rate': 0.1, 'minimum': 10, 'maximum': None},
                DocumentType.SERVICE_AGREEMENT: {'rate': 0.1, 'minimum': 10, 'maximum': None},
                DocumentType.CONVEYANCE: {'rate': 6.0, 'minimum': 100, 'maximum': None},
                DocumentType.LEASE: {'rate': 2.0, 'minimum': 100, 'maximum': None},
                DocumentType.MORTGAGE: {'rate': 0.5, 'minimum': 100, 'maximum': None},
                DocumentType.POWER_OF_ATTORNEY: {'rate': 0, 'minimum': 10, 'maximum': None},
                DocumentType.SHARE_TRANSFER: {'rate': 0.25, 'minimum': 100, 'maximum': None}
            },
            IndianState.KARNATAKA: {
                DocumentType.AGREEMENT: {'rate': 0.1, 'minimum': 10, 'maximum': None},
                DocumentType.SERVICE_AGREEMENT: {'rate': 0.1, 'minimum': 10, 'maximum': None},
                DocumentType.CONVEYANCE: {'rate': 5.0, 'minimum': 100, 'maximum': None},
                DocumentType.LEASE: {'rate': 1.0, 'minimum': 100, 'maximum': None},
                DocumentType.MORTGAGE: {'rate': 1.0, 'minimum': 100, 'maximum': None},
                DocumentType.POWER_OF_ATTORNEY: {'rate': 0, 'minimum': 10, 'maximum': None},
                DocumentType.SHARE_TRANSFER: {'rate': 0.25, 'minimum': 100, 'maximum': None}
            }
        }
        
    def _initialize_gst_database(self):
        """Initialize GST rates and HSN codes database."""
        self.gst_rates = {
            'services': {
                'legal_services': {'rate': 18.0, 'hsn': '998313'},
                'consulting_services': {'rate': 18.0, 'hsn': '998314'},
                'it_services': {'rate': 18.0, 'hsn': '998313'},
                'construction_services': {'rate': 18.0, 'hsn': '995411'},
                'financial_services': {'rate': 18.0, 'hsn': '997159'}
            },
            'goods': {
                'software': {'rate': 18.0, 'hsn': '852351'},
                'books': {'rate': 12.0, 'hsn': '490199'},
                'stationery': {'rate': 18.0, 'hsn': '482390'}
            }
        }
        
        self.gst_exemptions = [
            'educational services',
            'healthcare services',
            'agricultural services',
            'services by government',
            'charitable activities'
        ]
        
    def _initialize_monetary_patterns(self):
        """Initialize patterns for extracting Indian monetary amounts."""
        self.monetary_patterns = [
            # Rupees patterns
            r'(?:rs\.?\s*|rupees?\s*|inr\s*|₹\s*)(\d+(?:,\d{2,3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{2,3})*(?:\.\d{2})?)\s*(?:rs\.?|rupees?|inr|₹)',
            
            # Lakhs and crores patterns
            r'(\d+(?:\.\d+)?)\s*(?:lakhs?|lacs?)',
            r'(\d+(?:\.\d+)?)\s*crores?',
            r'(?:rs\.?\s*|rupees?\s*|₹\s*)(\d+(?:\.\d+)?)\s*(?:lakhs?|lacs?)',
            r'(?:rs\.?\s*|rupees?\s*|₹\s*)(\d+(?:\.\d+)?)\s*crores?',
            
            # Written amounts
            r'(?:rupees?\s+)?([a-z\s]+(?:lakh|crore|thousand|hundred)s?(?:\s+[a-z\s]+)*)\s*(?:only)?',
        ]
        
        # Number words mapping
        self.number_words = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
            'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
            'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
            'eighty': 80, 'ninety': 90, 'hundred': 100, 'thousand': 1000,
            'lakh': 100000, 'lac': 100000, 'crore': 10000000
        }
        
    def _initialize_compliance_rules(self):
        """Initialize compliance rules for Indian legal requirements."""
        self.mandatory_clauses = {
            DocumentType.AGREEMENT: [
                'consideration clause',
                'termination clause',
                'governing law clause',
                'dispute resolution clause'
            ],
            DocumentType.EMPLOYMENT: [
                'salary clause',
                'notice period clause',
                'confidentiality clause',
                'termination clause',
                'provident fund clause'
            ],
            DocumentType.LEASE: [
                'rent clause',
                'security deposit clause',
                'maintenance clause',
                'termination clause',
                'registration clause'
            ],
            DocumentType.LOAN_AGREEMENT: [
                'principal amount clause',
                'interest rate clause',
                'repayment schedule',
                'default clause',
                'security clause'
            ]
        }
        
        self.registration_requirements = {
            DocumentType.CONVEYANCE: {
                'required': True,
                'authority': 'Sub-Registrar',
                'time_limit': '4 months from execution',
                'base_fee': Decimal('1000'),
                'documents': ['original deed', 'identity proof', 'address proof', 'property documents']
            },
            DocumentType.LEASE: {
                'required': True,  # if lease > 11 months
                'authority': 'Sub-Registrar',
                'time_limit': '4 months from execution',
                'base_fee': Decimal('500'),
                'documents': ['lease deed', 'identity proof', 'property ownership proof']
            },
            DocumentType.MORTGAGE: {
                'required': True,
                'authority': 'Sub-Registrar',
                'time_limit': '4 months from execution',
                'base_fee': Decimal('1000'),
                'documents': ['mortgage deed', 'property documents', 'identity proof']
            },
            DocumentType.SHARE_TRANSFER: {
                'required': False,  # Generally not required for share transfers
                'authority': 'Company Registrar',
                'time_limit': 'As per company policy',
                'base_fee': Decimal('100'),
                'documents': ['share transfer deed', 'share certificates', 'identity proof']
            }
        }
    
    def analyze_document(self, text: str, state: Optional[IndianState] = None) -> IndianLegalAnalysis:
        """
        Perform comprehensive Indian legal analysis of a document.
        
        Args:
            text: Document text content
            state: Indian state for jurisdiction-specific analysis
            
        Returns:
            IndianLegalAnalysis with complete analysis results
        """
        if not text or not text.strip():
            return self._empty_analysis()
        
        # Detect state if not provided
        if not state:
            state = self._detect_state(text)
        
        # Perform various analyses
        act_references = self._extract_act_references(text)
        monetary_amounts = self._extract_monetary_amounts(text)
        document_type = self._detect_document_type(text)
        
        # Calculate stamp duty
        stamp_duty = self._calculate_stamp_duty(
            text, document_type, state, monetary_amounts
        )
        
        # Analyze GST implications
        gst_analysis = self._analyze_gst_implications(text, state)
        
        # Check compliance
        compliance_check = self._check_compliance(text, document_type)
        
        # Get registration requirements
        registration_reqs = self._get_registration_requirements(document_type, state)
        
        # Identify applicable laws
        applicable_laws = self._identify_applicable_laws(text, act_references)
        
        # Generate jurisdiction-specific notes
        jurisdiction_notes = self._generate_jurisdiction_notes(
            text, state, document_type, act_references
        )
        
        return IndianLegalAnalysis(
            act_references=act_references,
            stamp_duty=stamp_duty,
            gst_analysis=gst_analysis,
            monetary_amounts=monetary_amounts,
            compliance_check=compliance_check,
            registration_requirements=registration_reqs,
            applicable_laws=applicable_laws,
            jurisdiction_specific_notes=jurisdiction_notes
        )
    
    def _extract_act_references(self, text: str) -> List[ActReference]:
        """Extract references to Indian legal acts from the document."""
        references = []
        text_lower = text.lower()
        
        for act_name, act_data in self.indian_acts.items():
            for keyword in act_data['keywords']:
                if keyword in text_lower:
                    # Find sections mentioned
                    sections = self._find_sections_for_act(text, act_name)
                    
                    # Calculate confidence based on context
                    confidence = self._calculate_act_confidence(text_lower, keyword, sections)
                    
                    # Extract context around the reference
                    context = self._extract_context(text, keyword)
                    
                    # Extract year if mentioned
                    year = self._extract_year_from_act(act_name)
                    
                    references.append(ActReference(
                        act_name=act_name,
                        full_name=act_name,
                        year=year,
                        sections=sections,
                        confidence=confidence,
                        context=context
                    ))
                    break  # Avoid duplicate entries for same act
        
        return references
    
    def _extract_monetary_amounts(self, text: str) -> List[MonetaryAmount]:
        """Extract Indian monetary amounts from the document."""
        amounts = []
        
        for pattern in self.monetary_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_text = match.group(1) if match.groups() else match.group(0)
                    original_text = match.group(0)
                    
                    # Parse the amount
                    parsed_amount = self._parse_indian_amount(amount_text, original_text)
                    
                    if parsed_amount:
                        amounts.append(MonetaryAmount(
                            amount=parsed_amount,
                            currency='INR',
                            original_text=original_text,
                            formatted_amount=self._format_indian_amount(parsed_amount),
                            amount_in_words=self._amount_to_words(parsed_amount)
                        ))
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Failed to parse amount '{amount_text}': {e}")
                    continue
        
        # Remove duplicates and sort by amount
        unique_amounts = []
        seen_amounts = set()
        
        for amount in amounts:
            if amount.amount not in seen_amounts:
                unique_amounts.append(amount)
                seen_amounts.add(amount.amount)
        
        return sorted(unique_amounts, key=lambda x: x.amount, reverse=True)
    
    def _calculate_stamp_duty(
        self, 
        text: str, 
        document_type: DocumentType, 
        state: IndianState,
        monetary_amounts: List[MonetaryAmount]
    ) -> StampDutyAnalysis:
        """Calculate stamp duty for the document."""
        
        # Get consideration amount (highest monetary amount typically)
        consideration = monetary_amounts[0].amount if monetary_amounts else None
        
        # Get stamp duty rates for the state and document type
        state_rates = self.stamp_duty_rates.get(state, self.stamp_duty_rates[IndianState.DELHI])
        duty_info = state_rates.get(document_type, state_rates[DocumentType.AGREEMENT])
        
        # Calculate duty
        rate = duty_info['rate']
        minimum_duty = Decimal(str(duty_info['minimum']))
        maximum_duty = Decimal(str(duty_info['maximum'])) if duty_info['maximum'] else None
        
        calculated_duty = None
        if consideration:
            calculated_duty = consideration * Decimal(str(rate)) / Decimal('100')
            calculated_duty = max(calculated_duty, minimum_duty)
            if maximum_duty:
                calculated_duty = min(calculated_duty, maximum_duty)
        
        # Check for exemptions
        exemptions = self._check_stamp_duty_exemptions(text, document_type)
        
        # Generate requirements
        requirements = self._get_stamp_duty_requirements(document_type, state)
        
        # Determine compliance status
        compliance_status = self._determine_stamp_duty_compliance(text, calculated_duty)
        
        return StampDutyAnalysis(
            state=state,
            document_type=document_type,
            consideration_amount=consideration,
            stamp_duty_rate=rate,
            calculated_duty=calculated_duty,
            minimum_duty=minimum_duty,
            maximum_duty=maximum_duty,
            exemptions=exemptions,
            requirements=requirements,
            compliance_status=compliance_status
        )
    
    def _analyze_gst_implications(self, text: str, state: IndianState) -> GSTAnalysis:
        """Analyze GST implications for the document."""
        text_lower = text.lower()
        
        # Check if GST is applicable
        applicable = self._is_gst_applicable(text_lower)
        
        # Determine GST rate and HSN codes
        gst_rate, hsn_codes = self._determine_gst_rate_and_hsn(text_lower)
        
        # Determine place of supply
        place_of_supply = self._determine_place_of_supply(text, state)
        
        # Check for reverse charge
        reverse_charge = self._check_reverse_charge(text_lower)
        
        # Check for exemptions
        exemptions = self._check_gst_exemptions(text_lower)
        
        # Generate compliance requirements
        compliance_requirements = self._get_gst_compliance_requirements(applicable, gst_rate)
        
        # Check if GST registration is required
        registration_required = self._is_gst_registration_required(text_lower)
        
        return GSTAnalysis(
            applicable=applicable,
            gst_rate=gst_rate,
            hsn_codes=hsn_codes,
            place_of_supply=place_of_supply,
            reverse_charge=reverse_charge,
            exemptions=exemptions,
            compliance_requirements=compliance_requirements,
            registration_required=registration_required
        )
    
    def _check_compliance(self, text: str, document_type: DocumentType) -> ComplianceCheck:
        """Check compliance with Indian legal requirements."""
        text_lower = text.lower()
        
        # Get mandatory clauses for document type
        mandatory_clauses = self.mandatory_clauses.get(document_type, [])
        
        # Check for missing clauses
        missing_clauses = []
        for clause in mandatory_clauses:
            if not self._has_clause(text_lower, clause):
                missing_clauses.append(clause)
        
        # Identify violations
        violations = self._identify_violations(text_lower, document_type)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(missing_clauses, violations)
        
        # Determine compliance status
        compliant = len(missing_clauses) == 0 and len(violations) == 0
        
        # Assess risk level
        risk_level = self._assess_risk_level(missing_clauses, violations)
        
        return ComplianceCheck(
            compliant=compliant,
            violations=violations,
            recommendations=recommendations,
            mandatory_clauses=mandatory_clauses,
            missing_clauses=missing_clauses,
            risk_level=risk_level
        )
    
    # Helper methods implementation
    
    def _empty_analysis(self) -> IndianLegalAnalysis:
        """Return empty analysis for invalid input."""
        return IndianLegalAnalysis(
            act_references=[],
            stamp_duty=StampDutyAnalysis(
                state=IndianState.DELHI,
                document_type=DocumentType.OTHER,
                consideration_amount=None,
                stamp_duty_rate=0.0,
                calculated_duty=None,
                minimum_duty=Decimal('0'),
                maximum_duty=None,
                exemptions=[],
                requirements=[],
                compliance_status='unknown'
            ),
            gst_analysis=GSTAnalysis(
                applicable=False,
                gst_rate=None,
                hsn_codes=[],
                place_of_supply=None,
                reverse_charge=False,
                exemptions=[],
                compliance_requirements=[],
                registration_required=False
            ),
            monetary_amounts=[],
            compliance_check=ComplianceCheck(
                compliant=False,
                violations=[],
                recommendations=[],
                mandatory_clauses=[],
                missing_clauses=[],
                risk_level='unknown'
            ),
            registration_requirements=[],
            applicable_laws=[],
            jurisdiction_specific_notes=[]
        )
    
    def _detect_state(self, text: str) -> IndianState:
        """Detect Indian state from document text."""
        text_lower = text.lower()
        
        # Check for explicit state mentions
        for state in IndianState:
            if state.value.lower() in text_lower:
                return state
        
        # Default to Delhi if no state detected
        return IndianState.DELHI
    
    def _detect_document_type(self, text: str) -> DocumentType:
        """Detect document type from content with priority order."""
        text_lower = text.lower()
        
        # Document type keywords in priority order (more specific first)
        type_keywords = [
            (DocumentType.SHARE_TRANSFER, ['share transfer', 'share purchase', 'transfer of shares']),
            (DocumentType.CONVEYANCE, ['conveyance', 'sale deed', 'transfer deed']),
            (DocumentType.LEASE, ['lease deed', 'lease agreement', 'rental agreement', 'tenancy']),
            (DocumentType.MORTGAGE, ['mortgage', 'hypothecation']),
            (DocumentType.PARTNERSHIP, ['partnership deed', 'partnership']),
            (DocumentType.POWER_OF_ATTORNEY, ['power of attorney', 'poa']),
            (DocumentType.PROMISSORY_NOTE, ['promissory note', 'promise to pay']),
            (DocumentType.LOAN_AGREEMENT, ['loan agreement', 'loan', 'advance']),
            (DocumentType.SERVICE_AGREEMENT, ['service agreement']),
            (DocumentType.EMPLOYMENT, ['employment contract', 'employment', 'appointment letter', 'offer letter']),
            (DocumentType.NDA, ['non-disclosure agreement', 'confidentiality agreement', 'nda']),
            (DocumentType.AGREEMENT, ['agreement', 'contract'])  # Most generic, check last
        ]
        
        for doc_type, keywords in type_keywords:
            for keyword in keywords:
                if keyword in text_lower:
                    return doc_type
        
        return DocumentType.OTHER
    
    def _find_sections_for_act(self, text: str, act_name: str) -> List[str]:
        """Find specific sections mentioned for an act."""
        sections = []
        
        # Look for section patterns near act mentions
        section_patterns = [
            r'section\s+(\d+[a-z]?)',
            r'sec\.?\s+(\d+[a-z]?)',
            r's\.?\s+(\d+[a-z]?)',
            r'§\s*(\d+[a-z]?)'
        ]
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                sections.append(match.group(1))
        
        return list(set(sections))  # Remove duplicates
    
    def _calculate_act_confidence(self, text: str, keyword: str, sections: List[str]) -> float:
        """Calculate confidence score for act reference."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on context
        if len(sections) > 0:
            confidence += 0.3
        
        # Check for legal context words
        legal_context = ['pursuant to', 'under', 'in accordance with', 'as per', 'governed by']
        for context_word in legal_context:
            if context_word in text:
                confidence += 0.1
        
        return min(1.0, confidence)
    
    def _extract_context(self, text: str, keyword: str) -> str:
        """Extract context around a keyword."""
        try:
            index = text.lower().find(keyword.lower())
            if index == -1:
                return ""
            
            start = max(0, index - 100)
            end = min(len(text), index + len(keyword) + 100)
            return text[start:end].strip()
        except Exception:
            return ""
    
    def _extract_year_from_act(self, keyword: str) -> Optional[int]:
        """Extract year from act name."""
        year_match = re.search(r'\b(1\d{3}|20\d{2})\b', keyword)
        return int(year_match.group()) if year_match else None
    
    def _parse_indian_amount(self, amount_text: str, original_text: str) -> Optional[Decimal]:
        """Parse Indian monetary amount considering lakhs and crores."""
        try:
            # Remove commas and clean up
            clean_text = re.sub(r'[,\s]', '', amount_text.lower())
            
            # Handle written amounts
            if any(word in clean_text for word in ['lakh', 'crore', 'thousand', 'hundred']):
                return self._parse_written_amount(amount_text)
            
            # Handle numeric amounts
            numeric_match = re.search(r'(\d+(?:\.\d+)?)', clean_text)
            if not numeric_match:
                return None
            
            base_amount = Decimal(numeric_match.group(1))
            
            # Check for lakh/crore multipliers in original text
            original_lower = original_text.lower()
            if 'crore' in original_lower:
                return base_amount * Decimal('10000000')  # 1 crore = 10 million
            elif 'lakh' in original_lower or 'lac' in original_lower:
                return base_amount * Decimal('100000')  # 1 lakh = 100 thousand
            else:
                return base_amount
                
        except (ValueError, TypeError, AttributeError):
            return None
    
    def _parse_written_amount(self, text: str) -> Optional[Decimal]:
        """Parse written monetary amounts."""
        try:
            words = text.lower().split()
            total = Decimal('0')
            current = Decimal('0')
            
            for word in words:
                word = word.strip('.,')
                if word in self.number_words:
                    value = self.number_words[word]
                    if value == 100:
                        current *= Decimal(str(value))
                    elif value == 1000:
                        current *= Decimal(str(value))
                        total += current
                        current = Decimal('0')
                    elif value == 100000:  # lakh
                        current *= Decimal(str(value))
                        total += current
                        current = Decimal('0')
                    elif value == 10000000:  # crore
                        current *= Decimal(str(value))
                        total += current
                        current = Decimal('0')
                    else:
                        current += Decimal(str(value))
            
            return total + current if total + current > 0 else None
        except Exception:
            return None
    
    def _format_indian_amount(self, amount: Decimal) -> str:
        """Format amount in Indian numbering system."""
        if amount >= 10000000:  # 1 crore
            crores = amount / Decimal('10000000')
            return f"₹{crores:.2f} crores"
        elif amount >= 100000:  # 1 lakh
            lakhs = amount / Decimal('100000')
            return f"₹{lakhs:.2f} lakhs"
        else:
            return f"₹{amount:,.2f}"
    
    def _amount_to_words(self, amount: Decimal) -> str:
        """Convert amount to words (simplified implementation)."""
        # This is a simplified version - a full implementation would be more comprehensive
        if amount >= 10000000:
            crores = amount / Decimal('10000000')
            return f"{crores:.2f} crores"
        elif amount >= 100000:
            lakhs = amount / Decimal('100000')
            return f"{lakhs:.2f} lakhs"
        else:
            return f"{amount:,.2f} rupees"
    
    def _check_stamp_duty_exemptions(self, text: str, document_type: DocumentType) -> List[str]:
        """Check for stamp duty exemptions."""
        exemptions = []
        text_lower = text.lower()
        
        # Common exemptions
        if 'government' in text_lower or 'central government' in text_lower:
            exemptions.append('Government transaction exemption')
        
        if 'charitable' in text_lower or 'trust' in text_lower:
            exemptions.append('Charitable organization exemption')
        
        if document_type == DocumentType.POWER_OF_ATTORNEY and 'general' not in text_lower:
            exemptions.append('Specific power of attorney exemption')
        
        return exemptions
    
    def _get_stamp_duty_requirements(self, document_type: DocumentType, state: IndianState) -> List[str]:
        """Get stamp duty requirements for document type and state."""
        requirements = [
            f"Document must be executed on stamp paper of appropriate value",
            f"Stamp duty must be paid as per {state.value} Stamp Act",
            "Document should be properly stamped before execution"
        ]
        
        if document_type in [DocumentType.CONVEYANCE, DocumentType.LEASE, DocumentType.MORTGAGE]:
            requirements.append("Registration is mandatory within 4 months of execution")
        
        return requirements
    
    def _determine_stamp_duty_compliance(self, text: str, calculated_duty: Optional[Decimal]) -> str:
        """Determine stamp duty compliance status."""
        if 'stamp paper' in text.lower() or 'stamped' in text.lower():
            return 'compliant'
        elif calculated_duty and calculated_duty > 0:
            return 'requires_stamping'
        else:
            return 'unknown'
    
    def _is_gst_applicable(self, text: str) -> bool:
        """Check if GST is applicable to the transaction."""
        gst_indicators = [
            'supply of goods', 'supply of services', 'gst', 'service tax',
            'service provider', 'contractor', 'professional services',
            'legal services', 'consulting', 'advisory services',
            'software services', 'it services', 'construction services'
        ]
        
        return any(indicator in text for indicator in gst_indicators)
    
    def _determine_gst_rate_and_hsn(self, text: str) -> Tuple[Optional[float], List[str]]:
        """Determine GST rate and HSN codes based on document content."""
        # Simplified logic - in practice, this would be more sophisticated
        if 'legal services' in text or 'advocate' in text:
            return 18.0, ['998313']
        elif 'consulting' in text or 'advisory' in text:
            return 18.0, ['998314']
        elif 'software' in text or 'it services' in text:
            return 18.0, ['998313']
        elif 'construction' in text:
            return 18.0, ['995411']
        
        return None, []
    
    def _determine_place_of_supply(self, text: str, state: IndianState) -> Optional[str]:
        """Determine place of supply for GST purposes."""
        # Simplified - would need more sophisticated logic
        return state.value
    
    def _check_reverse_charge(self, text: str) -> bool:
        """Check if reverse charge mechanism applies."""
        reverse_charge_indicators = [
            'reverse charge', 'recipient liable', 'gst payable by recipient'
        ]
        
        return any(indicator in text for indicator in reverse_charge_indicators)
    
    def _check_gst_exemptions(self, text: str) -> List[str]:
        """Check for GST exemptions."""
        exemptions = []
        
        for exemption in self.gst_exemptions:
            if exemption in text:
                exemptions.append(exemption)
        
        return exemptions
    
    def _get_gst_compliance_requirements(self, applicable: bool, gst_rate: Optional[float]) -> List[str]:
        """Get GST compliance requirements."""
        if not applicable:
            return ['GST not applicable to this transaction']
        
        requirements = [
            'GST registration required if turnover exceeds threshold',
            'Proper GST invoice must be issued',
            'GST returns must be filed monthly/quarterly'
        ]
        
        if gst_rate:
            requirements.append(f'GST at {gst_rate}% must be charged and collected')
        
        return requirements
    
    def _is_gst_registration_required(self, text: str) -> bool:
        """Check if GST registration is required."""
        # Simplified logic
        return 'business' in text or 'services' in text or 'supply' in text
    
    def _has_clause(self, text: str, clause_type: str) -> bool:
        """Check if document has a specific type of clause."""
        clause_keywords = {
            'consideration clause': ['consideration', 'payment', 'amount', 'price'],
            'termination clause': ['termination', 'terminate', 'end', 'expiry'],
            'governing law clause': ['governing law', 'jurisdiction', 'courts of'],
            'dispute resolution clause': ['dispute', 'arbitration', 'mediation', 'resolution'],
            'salary clause': ['salary', 'remuneration', 'compensation', 'wages'],
            'notice period clause': ['notice period', 'notice', 'resignation'],
            'confidentiality clause': ['confidential', 'non-disclosure', 'proprietary'],
            'rent clause': ['rent', 'rental', 'lease amount'],
            'security deposit clause': ['security deposit', 'advance', 'deposit'],
            'maintenance clause': ['maintenance', 'repair', 'upkeep'],
            'principal amount clause': ['principal', 'loan amount', 'advance'],
            'interest rate clause': ['interest', 'rate', 'percentage'],
            'repayment schedule': ['repayment', 'installment', 'emi'],
            'default clause': ['default', 'breach', 'failure to pay'],
            'security clause': ['security', 'collateral', 'guarantee']
        }
        
        keywords = clause_keywords.get(clause_type, [])
        return any(keyword in text for keyword in keywords)
    
    def _identify_violations(self, text: str, document_type: DocumentType) -> List[str]:
        """Identify legal violations in the document."""
        violations = []
        
        # Check for common violations
        if 'illegal' in text or 'unlawful' in text:
            violations.append('Document contains references to illegal activities')
        
        if document_type == DocumentType.EMPLOYMENT:
            if 'below minimum wage' in text:
                violations.append('Salary below minimum wage requirements')
        
        if document_type == DocumentType.LEASE:
            if 'no registration' in text and 'more than 11 months' in text:
                violations.append('Lease exceeding 11 months requires registration')
        
        return violations
    
    def _generate_recommendations(self, missing_clauses: List[str], violations: List[str]) -> List[str]:
        """Generate recommendations based on missing clauses and violations."""
        recommendations = []
        
        for clause in missing_clauses:
            recommendations.append(f"Add {clause} to ensure legal compliance")
        
        for violation in violations:
            recommendations.append(f"Address violation: {violation}")
        
        if not missing_clauses and not violations:
            recommendations.append("Document appears to be legally compliant")
        
        return recommendations
    
    def _assess_risk_level(self, missing_clauses: List[str], violations: List[str]) -> str:
        """Assess overall risk level."""
        total_issues = len(missing_clauses) + len(violations)
        
        if total_issues == 0:
            return 'low'
        elif total_issues <= 2:
            return 'medium'
        else:
            return 'high'
    
    def _get_registration_requirements(self, document_type: DocumentType, state: IndianState) -> List[RegistrationRequirement]:
        """Get registration requirements for document type."""
        requirements = []
        
        if document_type in self.registration_requirements:
            req_data = self.registration_requirements[document_type]
            
            requirements.append(RegistrationRequirement(
                required=req_data['required'],
                authority=req_data['authority'],
                time_limit=req_data['time_limit'],
                fees=req_data['base_fee'],
                documents_needed=req_data['documents'],
                consequences_of_non_registration=[
                    'Document not admissible as evidence',
                    'Penalty for late registration',
                    'Legal enforceability issues'
                ]
            ))
        elif document_type == DocumentType.LEASE:
            # Special handling for lease - registration required if > 11 months
            requirements.append(RegistrationRequirement(
                required=True,
                authority='Sub-Registrar',
                time_limit='4 months from execution',
                fees=Decimal('500'),
                documents_needed=['lease deed', 'identity proof', 'property ownership proof'],
                consequences_of_non_registration=[
                    'Document not admissible as evidence',
                    'Penalty for late registration',
                    'Legal enforceability issues'
                ]
            ))
        
        return requirements
    
    def _identify_applicable_laws(self, text: str, act_references: List[ActReference]) -> List[str]:
        """Identify applicable laws based on document content and act references."""
        laws = []
        
        # Add laws from act references
        for ref in act_references:
            laws.append(ref.act_name)
        
        # Add other applicable laws based on content
        text_lower = text.lower()
        
        if 'contract' in text_lower or 'agreement' in text_lower:
            laws.append('Indian Contract Act, 1872')
        
        if 'property' in text_lower or 'sale' in text_lower:
            laws.append('Transfer of Property Act, 1882')
        
        if 'stamp' in text_lower:
            laws.append('Indian Stamp Act, 1899')
        
        if 'registration' in text_lower:
            laws.append('Registration Act, 1908')
        
        return list(set(laws))  # Remove duplicates
    
    def _generate_jurisdiction_notes(
        self, 
        text: str, 
        state: IndianState, 
        document_type: DocumentType,
        act_references: List[ActReference]
    ) -> List[str]:
        """Generate jurisdiction-specific notes and observations."""
        notes = []
        
        notes.append(f"Document analyzed under {state.value} jurisdiction")
        
        if document_type != DocumentType.OTHER:
            notes.append(f"Document identified as {document_type.value}")
        
        if act_references:
            notes.append(f"Found references to {len(act_references)} Indian legal acts")
        
        # State-specific notes
        if state == IndianState.MAHARASHTRA:
            notes.append("Maharashtra has specific stamp duty rates and registration requirements")
        elif state == IndianState.DELHI:
            notes.append("Delhi follows NCT stamp duty rates and registration procedures")
        elif state == IndianState.KARNATAKA:
            notes.append("Karnataka has e-stamping facility available for most document types")
        
        # Document type specific notes
        if document_type == DocumentType.LEASE:
            notes.append("Lease agreements exceeding 11 months require mandatory registration")
        elif document_type == DocumentType.CONVEYANCE:
            notes.append("Property conveyance requires registration within 4 months of execution")
        
        return notes