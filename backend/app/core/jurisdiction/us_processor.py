"""
US legal system processor.

Provides comprehensive analysis of US legal documents including federal regulations database,
USC and CFR citation extraction, UCC applicability detection, state law jurisdiction detection,
and securities and privacy law compliance verification.
"""

import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal, InvalidOperation
from datetime import datetime

logger = logging.getLogger(__name__)


class USState(Enum):
    """US states and territories for jurisdiction-specific processing."""
    ALABAMA = "Alabama"
    ALASKA = "Alaska"
    ARIZONA = "Arizona"
    ARKANSAS = "Arkansas"
    CALIFORNIA = "California"
    COLORADO = "Colorado"
    CONNECTICUT = "Connecticut"
    DELAWARE = "Delaware"
    FLORIDA = "Florida"
    GEORGIA = "Georgia"
    HAWAII = "Hawaii"
    IDAHO = "Idaho"
    ILLINOIS = "Illinois"
    INDIANA = "Indiana"
    IOWA = "Iowa"
    KANSAS = "Kansas"
    KENTUCKY = "Kentucky"
    LOUISIANA = "Louisiana"
    MAINE = "Maine"
    MARYLAND = "Maryland"
    MASSACHUSETTS = "Massachusetts"
    MICHIGAN = "Michigan"
    MINNESOTA = "Minnesota"
    MISSISSIPPI = "Mississippi"
    MISSOURI = "Missouri"
    MONTANA = "Montana"
    NEBRASKA = "Nebraska"
    NEVADA = "Nevada"
    NEW_HAMPSHIRE = "New Hampshire"
    NEW_JERSEY = "New Jersey"
    NEW_MEXICO = "New Mexico"
    NEW_YORK = "New York"
    NORTH_CAROLINA = "North Carolina"
    NORTH_DAKOTA = "North Dakota"
    OHIO = "Ohio"
    OKLAHOMA = "Oklahoma"
    OREGON = "Oregon"
    PENNSYLVANIA = "Pennsylvania"
    RHODE_ISLAND = "Rhode Island"
    SOUTH_CAROLINA = "South Carolina"
    SOUTH_DAKOTA = "South Dakota"
    TENNESSEE = "Tennessee"
    TEXAS = "Texas"
    UTAH = "Utah"
    VERMONT = "Vermont"
    VIRGINIA = "Virginia"
    WASHINGTON = "Washington"
    WEST_VIRGINIA = "West Virginia"
    WISCONSIN = "Wisconsin"
    WYOMING = "Wyoming"
    DISTRICT_OF_COLUMBIA = "District of Columbia"


class USDocumentType(Enum):
    """Types of US legal documents for analysis."""
    CONTRACT = "contract"
    EMPLOYMENT_AGREEMENT = "employment_agreement"
    NDA = "nda"
    PURCHASE_AGREEMENT = "purchase_agreement"
    LEASE_AGREEMENT = "lease_agreement"
    LOAN_AGREEMENT = "loan_agreement"
    PARTNERSHIP_AGREEMENT = "partnership_agreement"
    OPERATING_AGREEMENT = "operating_agreement"
    MERGER_AGREEMENT = "merger_agreement"
    SECURITIES_AGREEMENT = "securities_agreement"
    PRIVACY_POLICY = "privacy_policy"
    TERMS_OF_SERVICE = "terms_of_service"
    OTHER = "other"


@dataclass
class FederalLawReference:
    """Reference to US federal law found in the document."""
    law_name: str
    full_name: str
    citation: Optional[str]
    sections: List[str]
    confidence: float
    context: str


@dataclass
class UCCAnalysis:
    """UCC (Uniform Commercial Code) applicability and compliance analysis."""
    applicable: bool
    articles: List[str]
    transaction_type: Optional[str]
    state_variations: List[str]
    compliance_requirements: List[str]
    risk_factors: List[str]
    recommendations: List[str]


@dataclass
class SecuritiesAnalysis:
    """Securities law compliance analysis."""
    securities_involved: bool
    federal_exemptions: List[str]
    state_exemptions: List[str]
    registration_requirements: List[str]
    disclosure_requirements: List[str]
    compliance_status: str
    risk_level: str


@dataclass
class PrivacyAnalysis:
    """Privacy law compliance analysis (CCPA, GDPR, etc.)."""
    applicable_laws: List[str]
    data_types_processed: List[str]
    consent_requirements: List[str]
    disclosure_requirements: List[str]
    user_rights: List[str]
    compliance_gaps: List[str]
    recommendations: List[str]


@dataclass
class StateJurisdictionAnalysis:
    """State-specific jurisdiction and law analysis."""
    governing_state: Optional[USState]
    choice_of_law_clause: Optional[str]
    forum_selection_clause: Optional[str]
    state_specific_requirements: List[str]
    conflicts_of_law: List[str]
    enforceability_issues: List[str]


@dataclass
class MonetaryAmountUS:
    """Extracted US monetary amount."""
    amount: Decimal
    currency: str
    original_text: str
    formatted_amount: str


@dataclass
class USComplianceCheck:
    """US legal compliance checking results."""
    compliant: bool
    violations: List[str]
    recommendations: List[str]
    mandatory_clauses: List[str]
    missing_clauses: List[str]
    risk_level: str


@dataclass
class USLegalAnalysis:
    """Complete US legal analysis results."""
    federal_references: List[FederalLawReference]
    state_jurisdiction: StateJurisdictionAnalysis
    ucc_analysis: UCCAnalysis
    securities_analysis: SecuritiesAnalysis
    privacy_analysis: PrivacyAnalysis
    monetary_amounts: List[MonetaryAmountUS]
    compliance_check: USComplianceCheck
    applicable_laws: List[str]
    jurisdiction_specific_notes: List[str]


class USLegalProcessor:
    """
    US legal system processor with federal regulations database.
    
    Provides comprehensive analysis including USC and CFR citation extraction,
    UCC applicability detection, state law jurisdiction detection, and securities
    and privacy law compliance verification.
    """
    
    def __init__(self):
        """Initialize USLegalProcessor with legal databases and patterns."""
        self._initialize_federal_laws_database()
        self._initialize_ucc_database()
        self._initialize_securities_database()
        self._initialize_privacy_laws_database()
        self._initialize_state_law_patterns()
        self._initialize_monetary_patterns()
        self._initialize_compliance_rules()
        
    def _initialize_federal_laws_database(self):
        """Initialize comprehensive US federal laws database."""
        self.federal_laws = {
            'Securities Act of 1933': {
                'keywords': ['securities act of 1933', 'securities act 1933', '1933 act'],
                'citations': ['15 U.S.C. § 77a', '15 USC 77a'],
                'key_sections': {
                    '3': 'Exempted securities',
                    '4': 'Exempted transactions',
                    '5': 'Prohibitions relating to interstate commerce',
                    '11': 'Civil liabilities on account of false registration statement',
                    '12': 'Civil liabilities arising in connection with prospectuses'
                },
                'applicability': ['securities offerings', 'public offerings', 'private placements']
            },
            'Securities Exchange Act of 1934': {
                'keywords': ['securities exchange act', 'exchange act of 1934', '1934 act'],
                'citations': ['15 U.S.C. § 78a', '15 USC 78a'],
                'key_sections': {
                    '10': 'Manipulative and deceptive devices',
                    '13': 'Periodical and other reports',
                    '14': 'Proxies',
                    '16': 'Directors, officers, and principal stockholders'
                },
                'applicability': ['public companies', 'proxy statements', 'insider trading']
            },
            'Uniform Commercial Code': {
                'keywords': ['uniform commercial code', 'ucc', 'u.c.c.'],
                'citations': ['UCC'],
                'key_sections': {
                    'Article 1': 'General Provisions',
                    'Article 2': 'Sales',
                    'Article 3': 'Negotiable Instruments',
                    'Article 4': 'Bank Deposits',
                    'Article 9': 'Secured Transactions'
                },
                'applicability': ['commercial transactions', 'sales', 'secured transactions']
            },
            'Sarbanes-Oxley Act': {
                'keywords': ['sarbanes-oxley', 'sox', 'sarbox', 'sarbanes oxley act'],
                'citations': ['15 U.S.C. § 7201', 'Pub. L. 107-204'],
                'key_sections': {
                    '302': 'Corporate responsibility for financial reports',
                    '404': 'Management assessment of internal controls',
                    '906': 'Corporate responsibility for financial reports'
                },
                'applicability': ['public companies', 'financial reporting', 'internal controls']
            },
            'Dodd-Frank Act': {
                'keywords': ['dodd-frank', 'dodd frank act', 'financial reform act'],
                'citations': ['Pub. L. 111-203', '12 U.S.C. § 5301'],
                'key_sections': {
                    '619': 'Volcker Rule',
                    '1502': 'Conflict minerals disclosure',
                    '953': 'Executive compensation disclosure'
                },
                'applicability': ['financial institutions', 'executive compensation', 'derivatives']
            },
            'California Consumer Privacy Act': {
                'keywords': ['ccpa', 'california consumer privacy act', 'consumer privacy act'],
                'citations': ['Cal. Civ. Code § 1798.100'],
                'key_sections': {
                    '1798.100': 'Right to know',
                    '1798.105': 'Right to delete',
                    '1798.110': 'Right to know categories',
                    '1798.115': 'Right to know specific pieces'
                },
                'applicability': ['consumer data', 'privacy rights', 'data processing']
            },
            'Fair Labor Standards Act': {
                'keywords': ['flsa', 'fair labor standards act', 'wage and hour'],
                'citations': ['29 U.S.C. § 201', '29 USC 201'],
                'key_sections': {
                    '6': 'Minimum wage',
                    '7': 'Maximum hours',
                    '8': 'Overtime compensation'
                },
                'applicability': ['employment', 'wages', 'overtime', 'working hours']
            },
            'Americans with Disabilities Act': {
                'keywords': ['ada', 'americans with disabilities act', 'disability act'],
                'citations': ['42 U.S.C. § 12101', '42 USC 12101'],
                'key_sections': {
                    'Title I': 'Employment',
                    'Title II': 'Public services',
                    'Title III': 'Public accommodations'
                },
                'applicability': ['employment discrimination', 'accessibility', 'reasonable accommodation']
            }
        }
        
    def _initialize_ucc_database(self):
        """Initialize UCC articles and transaction types database."""
        self.ucc_articles = {
            'Article 1': {
                'title': 'General Provisions',
                'scope': 'Definitions and general principles',
                'keywords': ['general provisions', 'definitions', 'good faith']
            },
            'Article 2': {
                'title': 'Sales',
                'scope': 'Sale of goods',
                'keywords': ['sale of goods', 'merchant', 'warranty', 'delivery', 'acceptance']
            },
            'Article 2A': {
                'title': 'Leases',
                'scope': 'Leases of goods',
                'keywords': ['lease of goods', 'lessor', 'lessee', 'finance lease']
            },
            'Article 3': {
                'title': 'Negotiable Instruments',
                'scope': 'Promissory notes, drafts, checks',
                'keywords': ['promissory note', 'check', 'draft', 'negotiable instrument', 'holder in due course']
            },
            'Article 4': {
                'title': 'Bank Deposits and Collections',
                'scope': 'Bank collection process',
                'keywords': ['bank collection', 'depositary bank', 'collecting bank', 'payor bank']
            },
            'Article 4A': {
                'title': 'Funds Transfers',
                'scope': 'Wire transfers and electronic payments',
                'keywords': ['wire transfer', 'funds transfer', 'payment order', 'beneficiary bank']
            },
            'Article 5': {
                'title': 'Letters of Credit',
                'scope': 'Letters of credit',
                'keywords': ['letter of credit', 'issuer', 'beneficiary', 'applicant', 'documentary credit']
            },
            'Article 6': {
                'title': 'Bulk Transfers',
                'scope': 'Bulk sales (largely repealed)',
                'keywords': ['bulk transfer', 'bulk sale', 'creditor protection']
            },
            'Article 7': {
                'title': 'Warehouse Receipts, Bills of Lading',
                'scope': 'Documents of title',
                'keywords': ['warehouse receipt', 'bill of lading', 'document of title', 'bailee']
            },
            'Article 8': {
                'title': 'Investment Securities',
                'scope': 'Securities transactions',
                'keywords': ['investment securities', 'certificated security', 'uncertificated security', 'security entitlement']
            },
            'Article 9': {
                'title': 'Secured Transactions',
                'scope': 'Security interests in personal property',
                'keywords': ['security interest', 'collateral', 'debtor', 'secured party', 'financing statement', 'perfection']
            }
        }
        
        self.ucc_transaction_types = {
            'sale_of_goods': {
                'articles': ['Article 2'],
                'indicators': ['sale', 'purchase', 'goods', 'merchandise', 'products'],
                'requirements': ['offer', 'acceptance', 'consideration', 'delivery terms']
            },
            'secured_transaction': {
                'articles': ['Article 9'],
                'indicators': ['security interest', 'collateral', 'financing statement', 'secured party'],
                'requirements': ['security agreement', 'attachment', 'perfection', 'priority']
            },
            'negotiable_instrument': {
                'articles': ['Article 3'],
                'indicators': ['promissory note', 'check', 'draft', 'negotiable'],
                'requirements': ['unconditional promise', 'fixed amount', 'payable to order or bearer']
            },
            'lease_of_goods': {
                'articles': ['Article 2A'],
                'indicators': ['lease', 'lessor', 'lessee', 'rental'],
                'requirements': ['lease term', 'rental payments', 'return of goods']
            }
        }
        
    def _initialize_securities_database(self):
        """Initialize securities law database."""
        self.securities_exemptions = {
            'federal': {
                'Rule 506(b)': {
                    'description': 'Private placement to accredited investors',
                    'requirements': ['accredited investors', 'no general solicitation', 'disclosure requirements'],
                    'limitations': ['unlimited amount', '35 non-accredited investors max']
                },
                'Rule 506(c)': {
                    'description': 'Private placement with general solicitation',
                    'requirements': ['accredited investors only', 'verification of accreditation', 'general solicitation allowed'],
                    'limitations': ['unlimited amount', 'accredited investors only']
                },
                'Rule 504': {
                    'description': 'Small offering exemption',
                    'requirements': ['limited disclosure', 'state law compliance'],
                    'limitations': ['$10 million in 12 months', 'no public solicitation unless state allows']
                },
                'Regulation A+': {
                    'description': 'Mini-IPO exemption',
                    'requirements': ['SEC qualification', 'ongoing reporting', 'audited financials'],
                    'limitations': ['Tier 1: $20M, Tier 2: $75M in 12 months']
                }
            },
            'state': {
                'intrastate': {
                    'description': 'Intrastate offering exemption',
                    'requirements': ['residents of single state', 'doing business in state'],
                    'limitations': ['state residents only', 'resale restrictions']
                }
            }
        }
        
        self.securities_indicators = [
            'investment contract', 'security', 'stock', 'bond', 'note', 'debenture',
            'investment', 'profit sharing', 'common enterprise', 'efforts of others',
            'accredited investor', 'sophisticated investor', 'private placement',
            'offering memorandum', 'subscription agreement', 'securities exemption'
        ]
        
    def _initialize_privacy_laws_database(self):
        """Initialize privacy laws database."""
        self.privacy_laws = {
            'CCPA': {
                'full_name': 'California Consumer Privacy Act',
                'scope': 'California residents',
                'applicability': ['businesses with CA residents', 'annual revenue > $25M', 'personal info of 50K+ consumers'],
                'rights': ['right to know', 'right to delete', 'right to opt-out', 'right to non-discrimination'],
                'requirements': ['privacy policy', 'consumer request process', 'data inventory', 'opt-out mechanisms']
            },
            'CPRA': {
                'full_name': 'California Privacy Rights Act',
                'scope': 'California residents (CCPA amendment)',
                'applicability': ['enhanced CCPA requirements', 'sensitive personal information'],
                'rights': ['right to correct', 'right to limit use of sensitive PI'],
                'requirements': ['data protection assessments', 'enhanced disclosures', 'contractor agreements']
            },
            'GDPR': {
                'full_name': 'General Data Protection Regulation',
                'scope': 'EU residents',
                'applicability': ['EU data subjects', 'goods/services to EU', 'monitoring EU behavior'],
                'rights': ['access', 'rectification', 'erasure', 'portability', 'object to processing'],
                'requirements': ['lawful basis', 'consent mechanisms', 'data protection officer', 'impact assessments']
            },
            'COPPA': {
                'full_name': 'Children\'s Online Privacy Protection Act',
                'scope': 'Children under 13',
                'applicability': ['websites/services directed to children', 'actual knowledge of child users'],
                'rights': ['parental consent', 'parental access', 'parental deletion'],
                'requirements': ['verifiable parental consent', 'privacy policy', 'data minimization']
            },
            'HIPAA': {
                'full_name': 'Health Insurance Portability and Accountability Act',
                'scope': 'Protected health information',
                'applicability': ['covered entities', 'business associates', 'healthcare providers'],
                'rights': ['access to PHI', 'amendment rights', 'accounting of disclosures'],
                'requirements': ['administrative safeguards', 'physical safeguards', 'technical safeguards']
            }
        }
        
        self.privacy_data_types = [
            'personal information', 'personally identifiable information', 'pii',
            'sensitive personal information', 'biometric data', 'geolocation data',
            'health information', 'financial information', 'protected health information', 'phi',
            'consumer data', 'user data', 'customer data', 'behavioral data'
        ]
        
    def _initialize_state_law_patterns(self):
        """Initialize state law detection patterns."""
        self.governing_law_patterns = [
            r'governed\s+by\s+(?:the\s+)?laws?\s+of\s+(?:the\s+state\s+of\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'laws?\s+of\s+(?:the\s+state\s+of\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:shall\s+)?govern',
            r'under\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:state\s+)?law',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:corporate\s+)?law\s+(?:shall\s+)?govern',
            r'in\s+accordance\s+with\s+(?:the\s+)?laws?\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        self.forum_selection_patterns = [
            r'exclusive\s+jurisdiction\s+(?:of\s+)?(?:the\s+)?(?:courts?\s+(?:of\s+)?)?(?:in\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'courts?\s+(?:located\s+)?in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'venue\s+(?:shall\s+be\s+)?(?:in\s+)?(?:the\s+)?(?:courts?\s+of\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'submit\s+to\s+(?:the\s+)?(?:exclusive\s+)?jurisdiction\s+of\s+(?:the\s+)?(?:courts?\s+(?:of\s+)?)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'disputes\s+shall\s+be\s+resolved\s+in\s+(?:the\s+)?(?:courts?\s+of\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'courts?\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
    def _initialize_monetary_patterns(self):
        """Initialize US monetary amount patterns."""
        self.monetary_patterns = [
            r'\$\s*([\d,]+(?:\.\d{2})?)',
            r'(?:usd|dollars?)\s*([\d,]+(?:\.\d{2})?)',
            r'([\d,]+(?:\.\d{2})?)\s*(?:usd|dollars?)',
            r'(?:million|billion|trillion)\s*dollars?',
            r'\$\s*([\d,]+(?:\.\d{2})?)\s*(?:million|billion|trillion)?'
        ]
        
    def _initialize_compliance_rules(self):
        """Initialize US legal compliance rules."""
        self.mandatory_clauses = {
            USDocumentType.CONTRACT: [
                'consideration clause',
                'termination clause',
                'governing law clause',
                'dispute resolution clause',
                'force majeure clause'
            ],
            USDocumentType.EMPLOYMENT_AGREEMENT: [
                'compensation clause',
                'termination clause',
                'confidentiality clause',
                'non-compete clause',
                'benefits clause'
            ],
            USDocumentType.NDA: [
                'confidential information definition',
                'permitted disclosures',
                'return of information',
                'term and survival',
                'remedies clause'
            ],
            USDocumentType.SECURITIES_AGREEMENT: [
                'securities description',
                'purchase price',
                'representations and warranties',
                'conditions to closing',
                'indemnification'
            ],
            USDocumentType.PRIVACY_POLICY: [
                'information collection',
                'information use',
                'information sharing',
                'user rights',
                'contact information'
            ]
        }
    
    def analyze_document(self, text: str, state: Optional[USState] = None) -> USLegalAnalysis:
        """
        Perform comprehensive US legal analysis of a document.
        
        Args:
            text: Document text content
            state: US state for jurisdiction-specific analysis
            
        Returns:
            USLegalAnalysis with complete analysis results
        """
        if not text or not text.strip():
            return self._empty_analysis()
        
        # Detect governing state if not provided
        if not state:
            state = self._detect_governing_state(text)
        
        # Perform various analyses
        federal_references = self._extract_federal_law_references(text)
        monetary_amounts = self._extract_monetary_amounts(text)
        document_type = self._detect_document_type(text)
        
        # Analyze state jurisdiction
        state_jurisdiction = self._analyze_state_jurisdiction(text, state)
        
        # Analyze UCC applicability
        ucc_analysis = self._analyze_ucc_applicability(text)
        
        # Analyze securities law compliance
        securities_analysis = self._analyze_securities_compliance(text)
        
        # Analyze privacy law compliance
        privacy_analysis = self._analyze_privacy_compliance(text)
        
        # Check general compliance
        compliance_check = self._check_us_compliance(text, document_type)
        
        # Identify applicable laws
        applicable_laws = self._identify_applicable_us_laws(text, federal_references)
        
        # Generate jurisdiction-specific notes
        jurisdiction_notes = self._generate_us_jurisdiction_notes(
            text, state, document_type, federal_references
        )
        
        return USLegalAnalysis(
            federal_references=federal_references,
            state_jurisdiction=state_jurisdiction,
            ucc_analysis=ucc_analysis,
            securities_analysis=securities_analysis,
            privacy_analysis=privacy_analysis,
            monetary_amounts=monetary_amounts,
            compliance_check=compliance_check,
            applicable_laws=applicable_laws,
            jurisdiction_specific_notes=jurisdiction_notes
        )
    
    def _extract_federal_law_references(self, text: str) -> List[FederalLawReference]:
        """Extract references to US federal laws from the document."""
        references = []
        text_lower = text.lower()
        
        for law_name, law_data in self.federal_laws.items():
            for keyword in law_data['keywords']:
                if keyword in text_lower:
                    # Find sections mentioned
                    sections = self._find_sections_for_law(text, law_name)
                    
                    # Calculate confidence based on context
                    confidence = self._calculate_law_confidence(text_lower, keyword, sections)
                    
                    # Extract context around the reference
                    context = self._extract_context(text, keyword)
                    
                    # Find citation if present
                    citation = self._find_citation(text, law_data.get('citations', []))
                    
                    references.append(FederalLawReference(
                        law_name=law_name,
                        full_name=law_name,
                        citation=citation,
                        sections=sections,
                        confidence=confidence,
                        context=context
                    ))
                    break  # Avoid duplicate entries for same law
        
        return references
    
    def _analyze_state_jurisdiction(self, text: str, state: Optional[USState]) -> StateJurisdictionAnalysis:
        """Analyze state jurisdiction and choice of law."""
        
        # Detect governing state from choice of law clause
        governing_state = self._detect_governing_state(text) or state
        
        # Extract choice of law clause
        choice_of_law_clause = self._extract_choice_of_law_clause(text)
        
        # Extract forum selection clause
        forum_selection_clause = self._extract_forum_selection_clause(text)
        
        # Identify state-specific requirements
        state_requirements = self._identify_state_requirements(text, governing_state)
        
        # Check for conflicts of law issues
        conflicts = self._identify_conflicts_of_law(text, governing_state)
        
        # Assess enforceability issues
        enforceability_issues = self._assess_enforceability_issues(text, governing_state)
        
        return StateJurisdictionAnalysis(
            governing_state=governing_state,
            choice_of_law_clause=choice_of_law_clause,
            forum_selection_clause=forum_selection_clause,
            state_specific_requirements=state_requirements,
            conflicts_of_law=conflicts,
            enforceability_issues=enforceability_issues
        )
    
    def _analyze_ucc_applicability(self, text: str) -> UCCAnalysis:
        """Analyze UCC applicability and compliance."""
        text_lower = text.lower()
        
        # Determine if UCC applies
        applicable = self._is_ucc_applicable(text_lower)
        
        # Identify relevant UCC articles
        articles = self._identify_ucc_articles(text_lower)
        
        # Determine transaction type
        transaction_type = self._determine_ucc_transaction_type(text_lower)
        
        # Check for state variations
        state_variations = self._check_ucc_state_variations(text_lower)
        
        # Generate compliance requirements
        compliance_requirements = self._get_ucc_compliance_requirements(articles, transaction_type)
        
        # Identify risk factors
        risk_factors = self._identify_ucc_risk_factors(text_lower, articles)
        
        # Generate recommendations
        recommendations = self._generate_ucc_recommendations(risk_factors, compliance_requirements)
        
        return UCCAnalysis(
            applicable=applicable,
            articles=articles,
            transaction_type=transaction_type,
            state_variations=state_variations,
            compliance_requirements=compliance_requirements,
            risk_factors=risk_factors,
            recommendations=recommendations
        )
    
    def _analyze_securities_compliance(self, text: str) -> SecuritiesAnalysis:
        """Analyze securities law compliance."""
        text_lower = text.lower()
        
        # Check if securities are involved
        securities_involved = self._are_securities_involved(text_lower)
        
        # Identify federal exemptions
        federal_exemptions = self._identify_federal_exemptions(text_lower)
        
        # Identify state exemptions
        state_exemptions = self._identify_state_exemptions(text_lower)
        
        # Determine registration requirements
        registration_requirements = self._get_securities_registration_requirements(
            securities_involved, federal_exemptions
        )
        
        # Determine disclosure requirements
        disclosure_requirements = self._get_securities_disclosure_requirements(
            securities_involved, federal_exemptions
        )
        
        # Assess compliance status
        compliance_status = self._assess_securities_compliance_status(
            securities_involved, federal_exemptions, registration_requirements
        )
        
        # Assess risk level
        risk_level = self._assess_securities_risk_level(
            securities_involved, compliance_status, registration_requirements
        )
        
        return SecuritiesAnalysis(
            securities_involved=securities_involved,
            federal_exemptions=federal_exemptions,
            state_exemptions=state_exemptions,
            registration_requirements=registration_requirements,
            disclosure_requirements=disclosure_requirements,
            compliance_status=compliance_status,
            risk_level=risk_level
        )
    
    def _analyze_privacy_compliance(self, text: str) -> PrivacyAnalysis:
        """Analyze privacy law compliance."""
        text_lower = text.lower()
        
        # Identify applicable privacy laws
        applicable_laws = self._identify_applicable_privacy_laws(text_lower)
        
        # Identify data types processed
        data_types = self._identify_data_types_processed(text_lower)
        
        # Determine consent requirements
        consent_requirements = self._get_privacy_consent_requirements(applicable_laws, data_types)
        
        # Determine disclosure requirements
        disclosure_requirements = self._get_privacy_disclosure_requirements(applicable_laws)
        
        # Identify user rights
        user_rights = self._identify_privacy_user_rights(applicable_laws)
        
        # Identify compliance gaps
        compliance_gaps = self._identify_privacy_compliance_gaps(
            text_lower, applicable_laws, consent_requirements
        )
        
        # Generate recommendations
        recommendations = self._generate_privacy_recommendations(compliance_gaps, applicable_laws)
        
        return PrivacyAnalysis(
            applicable_laws=applicable_laws,
            data_types_processed=data_types,
            consent_requirements=consent_requirements,
            disclosure_requirements=disclosure_requirements,
            user_rights=user_rights,
            compliance_gaps=compliance_gaps,
            recommendations=recommendations
        )
    
    def _extract_monetary_amounts(self, text: str) -> List[MonetaryAmountUS]:
        """Extract US monetary amounts from the document."""
        amounts = []
        
        for pattern in self.monetary_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_text = match.group(1) if match.groups() else match.group(0)
                    original_text = match.group(0)
                    
                    # Parse the amount
                    parsed_amount = self._parse_us_amount(amount_text, original_text)
                    
                    if parsed_amount:
                        amounts.append(MonetaryAmountUS(
                            amount=parsed_amount,
                            currency='USD',
                            original_text=original_text,
                            formatted_amount=self._format_us_amount(parsed_amount)
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
    
    def _check_us_compliance(self, text: str, document_type: USDocumentType) -> USComplianceCheck:
        """Check compliance with US legal requirements."""
        text_lower = text.lower()
        
        # Get mandatory clauses for document type
        mandatory_clauses = self.mandatory_clauses.get(document_type, [])
        
        # Check for missing clauses
        missing_clauses = []
        for clause in mandatory_clauses:
            if not self._has_clause(text_lower, clause):
                missing_clauses.append(clause)
        
        # Identify violations
        violations = self._identify_us_violations(text_lower, document_type)
        
        # Generate recommendations
        recommendations = self._generate_us_recommendations(missing_clauses, violations)
        
        # Determine compliance status
        compliant = len(missing_clauses) == 0 and len(violations) == 0
        
        # Assess risk level
        risk_level = self._assess_us_risk_level(missing_clauses, violations)
        
        return USComplianceCheck(
            compliant=compliant,
            violations=violations,
            recommendations=recommendations,
            mandatory_clauses=mandatory_clauses,
            missing_clauses=missing_clauses,
            risk_level=risk_level
        )
    
    # Helper methods implementation
    
    def _empty_analysis(self) -> USLegalAnalysis:
        """Return empty analysis for invalid input."""
        return USLegalAnalysis(
            federal_references=[],
            state_jurisdiction=StateJurisdictionAnalysis(
                governing_state=None,
                choice_of_law_clause=None,
                forum_selection_clause=None,
                state_specific_requirements=[],
                conflicts_of_law=[],
                enforceability_issues=[]
            ),
            ucc_analysis=UCCAnalysis(
                applicable=False,
                articles=[],
                transaction_type=None,
                state_variations=[],
                compliance_requirements=[],
                risk_factors=[],
                recommendations=[]
            ),
            securities_analysis=SecuritiesAnalysis(
                securities_involved=False,
                federal_exemptions=[],
                state_exemptions=[],
                registration_requirements=[],
                disclosure_requirements=[],
                compliance_status='unknown',
                risk_level='unknown'
            ),
            privacy_analysis=PrivacyAnalysis(
                applicable_laws=[],
                data_types_processed=[],
                consent_requirements=[],
                disclosure_requirements=[],
                user_rights=[],
                compliance_gaps=[],
                recommendations=[]
            ),
            monetary_amounts=[],
            compliance_check=USComplianceCheck(
                compliant=False,
                violations=[],
                recommendations=[],
                mandatory_clauses=[],
                missing_clauses=[],
                risk_level='unknown'
            ),
            applicable_laws=[],
            jurisdiction_specific_notes=[]
        )
    
    def _detect_governing_state(self, text: str) -> Optional[USState]:
        """Detect governing state from choice of law clause."""
        # First try the governing law patterns
        for pattern in self.governing_law_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                potential_state = match.group(1).strip()
                # Check if it's a valid US state
                for state in USState:
                    if state.value.lower() == potential_state.lower():
                        return state
        
        # If no governing law pattern found, look for direct state mentions
        text_lower = text.lower()
        for state in USState:
            state_name = state.value.lower()
            # Look for state name in various contexts
            if (f"{state_name} law" in text_lower or 
                f"state of {state_name}" in text_lower or
                f"governed by {state_name}" in text_lower or
                f"laws of {state_name}" in text_lower):
                return state
        
        return None
    
    def _detect_document_type(self, text: str) -> USDocumentType:
        """Detect US document type from content."""
        text_lower = text.lower()
        
        # Document type keywords in priority order
        type_keywords = [
            (USDocumentType.SECURITIES_AGREEMENT, ['securities', 'investment', 'stock purchase', 'private placement']),
            (USDocumentType.PRIVACY_POLICY, ['privacy policy', 'data collection', 'personal information']),
            (USDocumentType.TERMS_OF_SERVICE, ['terms of service', 'terms of use', 'user agreement']),
            (USDocumentType.EMPLOYMENT_AGREEMENT, ['employment agreement', 'employment contract', 'offer letter']),
            (USDocumentType.NDA, ['non-disclosure', 'confidentiality agreement', 'nda']),
            (USDocumentType.MERGER_AGREEMENT, ['merger agreement', 'acquisition agreement', 'merger']),
            (USDocumentType.OPERATING_AGREEMENT, ['operating agreement', 'llc agreement']),
            (USDocumentType.PARTNERSHIP_AGREEMENT, ['partnership agreement', 'partnership']),
            (USDocumentType.LOAN_AGREEMENT, ['loan agreement', 'credit agreement', 'promissory note']),
            (USDocumentType.LEASE_AGREEMENT, ['lease agreement', 'rental agreement', 'lease']),
            (USDocumentType.PURCHASE_AGREEMENT, ['purchase agreement', 'sale agreement', 'asset purchase']),
            (USDocumentType.CONTRACT, ['contract', 'agreement'])
        ]
        
        for doc_type, keywords in type_keywords:
            for keyword in keywords:
                if keyword in text_lower:
                    return doc_type
        
        return USDocumentType.OTHER   
 
    def _find_sections_for_law(self, text: str, law_name: str) -> List[str]:
        """Find specific sections mentioned for a law."""
        sections = []
        
        # Look for section patterns near the law name
        law_data = self.federal_laws.get(law_name, {})
        key_sections = law_data.get('key_sections', {})
        
        for section_num in key_sections.keys():
            # Look for various section reference patterns
            patterns = [
                rf'section\s+{re.escape(section_num)}\b',
                rf'§\s*{re.escape(section_num)}\b',
                rf'{re.escape(section_num)}\([a-z]\)',
                rf'subsection\s+{re.escape(section_num)}'
            ]
            
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    sections.append(section_num)
                    break
        
        return sections
    
    def _calculate_law_confidence(self, text_lower: str, keyword: str, sections: List[str]) -> float:
        """Calculate confidence score for law reference."""
        confidence = 0.5  # Base confidence for keyword match
        
        # Increase confidence based on context
        keyword_index = text_lower.find(keyword)
        if keyword_index != -1:
            # Check surrounding context (100 chars before and after)
            start = max(0, keyword_index - 100)
            end = min(len(text_lower), keyword_index + len(keyword) + 100)
            context = text_lower[start:end]
            
            # Legal context indicators
            legal_indicators = ['pursuant to', 'under', 'in accordance with', 'compliance with', 'violation of']
            for indicator in legal_indicators:
                if indicator in context:
                    confidence += 0.2
            
            # Section references increase confidence
            confidence += len(sections) * 0.1
            
            # Citation patterns increase confidence
            if re.search(r'\d+\s+u\.?s\.?c\.?\s+§?\s*\d+', context):
                confidence += 0.3
        
        return min(1.0, confidence)
    
    def _extract_context(self, text: str, keyword: str) -> str:
        """Extract context around a keyword."""
        keyword_index = text.lower().find(keyword.lower())
        if keyword_index == -1:
            return ""
        
        # Extract 200 characters before and after
        start = max(0, keyword_index - 200)
        end = min(len(text), keyword_index + len(keyword) + 200)
        
        return text[start:end].strip()
    
    def _find_citation(self, text: str, citations: List[str]) -> Optional[str]:
        """Find legal citation in text."""
        for citation in citations:
            if citation.lower() in text.lower():
                return citation
        
        # Look for USC patterns
        usc_pattern = r'\d+\s+U\.?S\.?C\.?\s+§?\s*\d+'
        match = re.search(usc_pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
        
        return None
    
    def _extract_choice_of_law_clause(self, text: str) -> Optional[str]:
        """Extract choice of law clause from document."""
        for pattern in self.governing_law_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract the full sentence containing the match
                sentence_start = text.rfind('.', 0, match.start()) + 1
                sentence_end = text.find('.', match.end())
                if sentence_end == -1:
                    sentence_end = len(text)
                
                return text[sentence_start:sentence_end].strip()
        
        return None
    
    def _extract_forum_selection_clause(self, text: str) -> Optional[str]:
        """Extract forum selection clause from document."""
        for pattern in self.forum_selection_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract the full sentence containing the match
                sentence_start = text.rfind('.', 0, match.start()) + 1
                sentence_end = text.find('.', match.end())
                if sentence_end == -1:
                    sentence_end = len(text)
                
                return text[sentence_start:sentence_end].strip()
        
        return None
    
    def _identify_state_requirements(self, text: str, state: Optional[USState]) -> List[str]:
        """Identify state-specific legal requirements."""
        requirements = []
        text_lower = text.lower()
        
        if not state:
            return requirements
        
        # State-specific requirements based on common patterns
        state_specific_patterns = {
            USState.DELAWARE: [
                'delaware corporate law requirements',
                'delaware general corporation law compliance',
                'board resolutions required'
            ],
            USState.CALIFORNIA: [
                'california corporations code compliance',
                'california consumer privacy act compliance',
                'california employment law requirements'
            ],
            USState.NEW_YORK: [
                'new york business corporation law',
                'new york employment requirements',
                'new york consumer protection'
            ]
        }
        
        if state in state_specific_patterns:
            for requirement in state_specific_patterns[state]:
                # Check if document type suggests this requirement applies
                if any(keyword in text_lower for keyword in requirement.lower().split()):
                    requirements.append(requirement)
        
        return requirements
    
    def _identify_conflicts_of_law(self, text: str, state: Optional[USState]) -> List[str]:
        """Identify potential conflicts of law issues."""
        conflicts = []
        text_lower = text.lower()
        
        # Check for multiple state references
        mentioned_states = []
        for us_state in USState:
            if us_state.value.lower() in text_lower:
                mentioned_states.append(us_state.value)
        
        if len(mentioned_states) > 1:
            conflicts.append(f"Multiple states mentioned: {', '.join(mentioned_states)}")
        
        # Check for federal vs state law conflicts
        if 'federal law' in text_lower and 'state law' in text_lower:
            conflicts.append("Potential federal and state law conflict")
        
        return conflicts
    
    def _assess_enforceability_issues(self, text: str, state: Optional[USState]) -> List[str]:
        """Assess potential enforceability issues."""
        issues = []
        text_lower = text.lower()
        
        # Check for common enforceability problems
        if 'unconscionable' in text_lower:
            issues.append("Potential unconscionability issue")
        
        if 'penalty' in text_lower and 'liquidated damages' not in text_lower:
            issues.append("Potential unenforceable penalty clause")
        
        if 'non-compete' in text_lower or 'restraint of trade' in text_lower:
            issues.append("Non-compete clause may have enforceability issues")
        
        return issues
    
    def _is_ucc_applicable(self, text_lower: str) -> bool:
        """Determine if UCC applies to the document."""
        ucc_indicators = [
            'sale of goods', 'goods', 'merchandise', 'products',
            'security interest', 'collateral', 'secured party',
            'negotiable instrument', 'promissory note', 'check',
            'lease of goods', 'commercial transaction'
        ]
        
        return any(indicator in text_lower for indicator in ucc_indicators)
    
    def _identify_ucc_articles(self, text_lower: str) -> List[str]:
        """Identify relevant UCC articles."""
        applicable_articles = []
        
        for article, data in self.ucc_articles.items():
            keywords = data['keywords']
            if any(keyword in text_lower for keyword in keywords):
                applicable_articles.append(article)
        
        return applicable_articles
    
    def _determine_ucc_transaction_type(self, text_lower: str) -> Optional[str]:
        """Determine UCC transaction type."""
        for transaction_type, data in self.ucc_transaction_types.items():
            indicators = data['indicators']
            if any(indicator in text_lower for indicator in indicators):
                return transaction_type.replace('_', ' ').title()
        
        return None
    
    def _check_ucc_state_variations(self, text_lower: str) -> List[str]:
        """Check for UCC state law variations."""
        variations = []
        
        # Common state variations
        if 'louisiana' in text_lower:
            variations.append("Louisiana has not adopted UCC Article 2 (uses Civil Code)")
        
        if 'california' in text_lower and 'warranty' in text_lower:
            variations.append("California has additional warranty requirements")
        
        return variations
    
    def _get_ucc_compliance_requirements(self, articles: List[str], transaction_type: Optional[str]) -> List[str]:
        """Get UCC compliance requirements."""
        requirements = []
        
        if 'Article 2' in articles:
            requirements.extend([
                'Offer and acceptance requirements',
                'Consideration requirements',
                'Warranty provisions',
                'Risk of loss allocation'
            ])
        
        if 'Article 9' in articles:
            requirements.extend([
                'Security agreement execution',
                'Attachment of security interest',
                'Perfection requirements',
                'Priority rules compliance'
            ])
        
        if 'Article 3' in articles:
            requirements.extend([
                'Negotiability requirements',
                'Holder in due course status',
                'Proper endorsement'
            ])
        
        return requirements
    
    def _identify_ucc_risk_factors(self, text_lower: str, articles: List[str]) -> List[str]:
        """Identify UCC-related risk factors."""
        risks = []
        
        if 'Article 2' in articles:
            if 'warranty disclaimer' not in text_lower:
                risks.append("No warranty disclaimer - implied warranties may apply")
            
            if 'delivery terms' not in text_lower and 'fob' not in text_lower:
                risks.append("Unclear delivery terms - risk of loss allocation uncertain")
        
        if 'Article 9' in articles:
            if 'financing statement' not in text_lower:
                risks.append("No mention of financing statement filing")
            
            if 'default' not in text_lower:
                risks.append("No default provisions specified")
        
        return risks
    
    def _generate_ucc_recommendations(self, risk_factors: List[str], requirements: List[str]) -> List[str]:
        """Generate UCC compliance recommendations."""
        recommendations = []
        
        if risk_factors:
            recommendations.append("Address identified risk factors to ensure UCC compliance")
        
        if requirements:
            recommendations.append("Ensure all UCC requirements are met for transaction type")
        
        recommendations.extend([
            "Consider state law variations that may apply",
            "Review warranty and disclaimer provisions",
            "Ensure proper documentation for enforceability"
        ])
        
        return recommendations
    
    def _are_securities_involved(self, text_lower: str) -> bool:
        """Check if securities are involved in the document."""
        return any(indicator in text_lower for indicator in self.securities_indicators)
    
    def _identify_federal_exemptions(self, text_lower: str) -> List[str]:
        """Identify federal securities exemptions."""
        exemptions = []
        
        for exemption_name, data in self.securities_exemptions['federal'].items():
            # Check for exemption keywords
            exemption_keywords = exemption_name.lower().split()
            if all(keyword in text_lower for keyword in exemption_keywords):
                exemptions.append(exemption_name)
        
        # Check for common exemption terms
        if 'private placement' in text_lower:
            exemptions.append('Private Placement (Rule 506)')
        
        if 'accredited investor' in text_lower:
            exemptions.append('Accredited Investor Exemption')
        
        return exemptions
    
    def _identify_state_exemptions(self, text_lower: str) -> List[str]:
        """Identify state securities exemptions."""
        exemptions = []
        
        if 'intrastate' in text_lower:
            exemptions.append('Intrastate Offering Exemption')
        
        if 'small offering' in text_lower:
            exemptions.append('Small Offering Exemption')
        
        return exemptions
    
    def _get_securities_registration_requirements(self, securities_involved: bool, exemptions: List[str]) -> List[str]:
        """Get securities registration requirements."""
        if not securities_involved:
            return []
        
        if exemptions:
            return [f"Comply with {exemption} requirements" for exemption in exemptions]
        
        return [
            'SEC registration required',
            'State registration may be required',
            'Prospectus delivery required',
            'Ongoing reporting obligations'
        ]
    
    def _get_securities_disclosure_requirements(self, securities_involved: bool, exemptions: List[str]) -> List[str]:
        """Get securities disclosure requirements."""
        if not securities_involved:
            return []
        
        requirements = []
        
        if 'Rule 506' in str(exemptions):
            requirements.extend([
                'Private placement memorandum',
                'Risk factor disclosures',
                'Financial statement requirements'
            ])
        
        if not exemptions:
            requirements.extend([
                'Registration statement',
                'Prospectus',
                'Periodic reports (10-K, 10-Q, 8-K)'
            ])
        
        return requirements
    
    def _assess_securities_compliance_status(self, securities_involved: bool, exemptions: List[str], requirements: List[str]) -> str:
        """Assess securities compliance status."""
        if not securities_involved:
            return 'Not applicable'
        
        if exemptions and requirements:
            return 'Exemption available - compliance required'
        elif exemptions:
            return 'Exemption may apply'
        else:
            return 'Registration likely required'
    
    def _assess_securities_risk_level(self, securities_involved: bool, compliance_status: str, requirements: List[str]) -> str:
        """Assess securities law risk level."""
        if not securities_involved:
            return 'Low'
        
        if 'registration likely required' in compliance_status.lower():
            return 'High'
        elif 'compliance required' in compliance_status.lower():
            return 'Medium'
        else:
            return 'Low'
    
    def _identify_applicable_privacy_laws(self, text_lower: str) -> List[str]:
        """Identify applicable privacy laws."""
        applicable = []
        
        for law_code, law_data in self.privacy_laws.items():
            # Check scope and applicability
            scope_keywords = law_data['scope'].lower().split()
            if any(keyword in text_lower for keyword in scope_keywords):
                applicable.append(law_code)
        
        # Check for specific privacy law mentions
        if 'ccpa' in text_lower or 'california consumer privacy' in text_lower:
            applicable.append('CCPA')
        
        if 'gdpr' in text_lower or 'general data protection' in text_lower:
            applicable.append('GDPR')
        
        if 'coppa' in text_lower or 'children' in text_lower:
            applicable.append('COPPA')
        
        if 'hipaa' in text_lower or 'health information' in text_lower:
            applicable.append('HIPAA')
        
        return list(set(applicable))  # Remove duplicates
    
    def _identify_data_types_processed(self, text_lower: str) -> List[str]:
        """Identify types of data processed."""
        data_types = []
        
        for data_type in self.privacy_data_types:
            if data_type in text_lower:
                data_types.append(data_type)
        
        return data_types
    
    def _get_privacy_consent_requirements(self, laws: List[str], data_types: List[str]) -> List[str]:
        """Get privacy consent requirements."""
        requirements = []
        
        if 'CCPA' in laws:
            requirements.extend([
                'Opt-out mechanism for sale of personal information',
                'Clear privacy policy disclosure',
                'Consumer request handling process'
            ])
        
        if 'GDPR' in laws:
            requirements.extend([
                'Lawful basis for processing',
                'Explicit consent for sensitive data',
                'Consent withdrawal mechanism'
            ])
        
        if 'COPPA' in laws:
            requirements.extend([
                'Verifiable parental consent',
                'Parental notification',
                'Limited data collection from children'
            ])
        
        return requirements
    
    def _get_privacy_disclosure_requirements(self, laws: List[str]) -> List[str]:
        """Get privacy disclosure requirements."""
        requirements = []
        
        if 'CCPA' in laws:
            requirements.extend([
                'Categories of personal information collected',
                'Purposes for collection and use',
                'Third parties with whom information is shared',
                'Consumer rights and how to exercise them'
            ])
        
        if 'GDPR' in laws:
            requirements.extend([
                'Identity and contact details of controller',
                'Purposes and legal basis for processing',
                'Data retention periods',
                'Data subject rights'
            ])
        
        return requirements
    
    def _identify_privacy_user_rights(self, laws: List[str]) -> List[str]:
        """Identify privacy user rights."""
        rights = []
        
        for law in laws:
            if law in self.privacy_laws:
                rights.extend(self.privacy_laws[law]['rights'])
        
        return list(set(rights))  # Remove duplicates
    
    def _identify_privacy_compliance_gaps(self, text_lower: str, laws: List[str], requirements: List[str]) -> List[str]:
        """Identify privacy compliance gaps."""
        gaps = []
        
        # Check if required elements are missing
        if 'CCPA' in laws:
            if 'opt-out' not in text_lower and 'do not sell' not in text_lower:
                gaps.append('Missing CCPA opt-out mechanism')
            
            if 'consumer rights' not in text_lower:
                gaps.append('Missing consumer rights disclosure')
        
        if 'GDPR' in laws:
            if 'lawful basis' not in text_lower:
                gaps.append('Missing GDPR lawful basis disclosure')
            
            if 'data protection officer' not in text_lower and 'dpo' not in text_lower:
                gaps.append('Missing data protection officer contact')
        
        return gaps
    
    def _generate_privacy_recommendations(self, gaps: List[str], laws: List[str]) -> List[str]:
        """Generate privacy compliance recommendations."""
        recommendations = []
        
        if gaps:
            recommendations.append("Address identified compliance gaps")
        
        for law in laws:
            if law == 'CCPA':
                recommendations.append("Implement CCPA-compliant privacy policy and consumer request process")
            elif law == 'GDPR':
                recommendations.append("Ensure GDPR compliance including lawful basis and data subject rights")
            elif law == 'COPPA':
                recommendations.append("Implement parental consent mechanisms for children's data")
        
        return recommendations
    
    def _parse_us_amount(self, amount_text: str, original_text: str) -> Optional[Decimal]:
        """Parse US monetary amount."""
        try:
            # Remove commas and dollar signs
            clean_amount = re.sub(r'[,$]', '', amount_text)
            
            # Handle million/billion/trillion
            multiplier = 1
            if 'million' in original_text.lower():
                multiplier = 1_000_000
            elif 'billion' in original_text.lower():
                multiplier = 1_000_000_000
            elif 'trillion' in original_text.lower():
                multiplier = 1_000_000_000_000
            
            amount = Decimal(clean_amount) * multiplier
            return amount
        except (ValueError, InvalidOperation):
            return None
    
    def _format_us_amount(self, amount: Decimal) -> str:
        """Format US amount for display."""
        if amount >= 1_000_000_000:
            return f"${amount / 1_000_000_000:.2f}B"
        elif amount >= 1_000_000:
            return f"${amount / 1_000_000:.2f}M"
        elif amount >= 1_000:
            return f"${amount / 1_000:.2f}K"
        else:
            return f"${amount:.2f}"
    
    def _has_clause(self, text_lower: str, clause: str) -> bool:
        """Check if document has a specific clause."""
        clause_keywords = clause.lower().split()
        return any(keyword in text_lower for keyword in clause_keywords)
    
    def _identify_us_violations(self, text_lower: str, document_type: USDocumentType) -> List[str]:
        """Identify US legal violations."""
        violations = []
        
        # Check for common violations based on document type
        if document_type == USDocumentType.EMPLOYMENT_AGREEMENT:
            if 'at-will' not in text_lower and 'termination' in text_lower:
                violations.append("Missing at-will employment disclaimer")
        
        if document_type == USDocumentType.SECURITIES_AGREEMENT:
            if 'accredited investor' not in text_lower and 'private placement' in text_lower:
                violations.append("Private placement without accredited investor verification")
        
        return violations
    
    def _generate_us_recommendations(self, missing_clauses: List[str], violations: List[str]) -> List[str]:
        """Generate US legal recommendations."""
        recommendations = []
        
        if missing_clauses:
            recommendations.append(f"Add missing mandatory clauses: {', '.join(missing_clauses)}")
        
        if violations:
            recommendations.append("Address identified legal violations")
        
        recommendations.extend([
            "Review governing law and jurisdiction clauses",
            "Ensure compliance with applicable federal and state laws",
            "Consider dispute resolution mechanisms"
        ])
        
        return recommendations
    
    def _assess_us_risk_level(self, missing_clauses: List[str], violations: List[str]) -> str:
        """Assess US legal risk level."""
        total_issues = len(missing_clauses) + len(violations)
        
        if total_issues >= 5:
            return 'High'
        elif total_issues >= 3:
            return 'Medium'
        elif total_issues >= 1:
            return 'Low'
        else:
            return 'Minimal'
    
    def _identify_applicable_us_laws(self, text: str, federal_references: List[FederalLawReference]) -> List[str]:
        """Identify applicable US laws."""
        laws = []
        
        # Add federal laws from references
        for ref in federal_references:
            laws.append(ref.law_name)
        
        # Add common law principles
        text_lower = text.lower()
        if 'contract' in text_lower:
            laws.append('Contract Law')
        
        if 'tort' in text_lower or 'negligence' in text_lower:
            laws.append('Tort Law')
        
        if 'employment' in text_lower:
            laws.append('Employment Law')
        
        return list(set(laws))  # Remove duplicates
    
    def _generate_us_jurisdiction_notes(
        self, 
        text: str, 
        state: Optional[USState], 
        document_type: USDocumentType,
        federal_references: List[FederalLawReference]
    ) -> List[str]:
        """Generate US jurisdiction-specific notes."""
        notes = []
        
        if state:
            notes.append(f"Document appears to be governed by {state.value} law")
        
        if federal_references:
            notes.append(f"Document references {len(federal_references)} federal law(s)")
        
        # Document type specific notes
        if document_type == USDocumentType.SECURITIES_AGREEMENT:
            notes.append("Securities law compliance required - consider federal and state exemptions")
        
        if document_type == USDocumentType.EMPLOYMENT_AGREEMENT:
            notes.append("Employment law compliance varies by state - review local requirements")
        
        return notes