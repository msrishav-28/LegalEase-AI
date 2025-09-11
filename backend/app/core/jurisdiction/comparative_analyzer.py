"""
Comparative jurisdiction analyzer for cross-border legal analysis.

Provides comprehensive comparison between Indian and US legal requirements,
enforceability analysis, formalities comparison, tax implications analysis,
and recommendations for cross-border transactions.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union
from decimal import Decimal
from datetime import datetime

from .indian_processor import IndianLegalProcessor, IndianLegalAnalysis, IndianState
from .us_processor import USLegalProcessor, USLegalAnalysis, USState

logger = logging.getLogger(__name__)


class EnforceabilityRisk(Enum):
    """Risk levels for enforceability."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceGap(Enum):
    """Types of compliance gaps."""
    FORMALITY = "formality"
    REGISTRATION = "registration"
    TAX = "tax"
    DISCLOSURE = "disclosure"
    GOVERNING_LAW = "governing_law"
    DISPUTE_RESOLUTION = "dispute_resolution"


@dataclass
class EnforceabilityComparison:
    """Comparison of enforceability between jurisdictions."""
    india_enforceability: Dict[str, Any]
    us_enforceability: Dict[str, Any]
    cross_border_risks: List[str]
    enforceability_score: Dict[str, float]  # India vs US scores
    recommendations: List[str]
    risk_level: EnforceabilityRisk


@dataclass
class FormalitiesComparison:
    """Comparison of legal formalities between jurisdictions."""
    stamp_duty_comparison: Dict[str, Any]
    registration_comparison: Dict[str, Any]
    witness_requirements: Dict[str, Any]
    notarization_requirements: Dict[str, Any]
    execution_formalities: Dict[str, Any]
    compliance_gaps: List[str]


@dataclass
class TaxImplications:
    """Tax implications analysis for cross-border transactions."""
    india_tax_implications: Dict[str, Any]
    us_tax_implications: Dict[str, Any]
    dtaa_benefits: List[str]  # Double Taxation Avoidance Agreement
    withholding_tax: Dict[str, Any]
    transfer_pricing: Dict[str, Any]
    gst_implications: Dict[str, Any]
    recommendations: List[str]


@dataclass
class CrossBorderRecommendation:
    """Recommendation for cross-border transactions."""
    category: str
    priority: str  # high, medium, low
    description: str
    rationale: str
    implementation_steps: List[str]
    estimated_cost: Optional[str]
    timeline: Optional[str]


@dataclass
class JurisdictionComplianceGap:
    """Compliance gap between jurisdictions."""
    gap_type: ComplianceGap
    description: str
    india_requirement: str
    us_requirement: str
    impact: str
    mitigation_strategy: str
    priority: str


@dataclass
class CrossBorderAnalysis:
    """Complete cross-border legal analysis results."""
    enforceability_comparison: EnforceabilityComparison
    formalities_comparison: FormalitiesComparison
    tax_implications: TaxImplications
    recommended_governing_law: str
    recommended_dispute_resolution: str
    compliance_gaps: List[JurisdictionComplianceGap]
    recommendations: List[CrossBorderRecommendation]
    overall_risk_assessment: str
    implementation_roadmap: List[str]


class ComparativeJurisdictionAnalyzer:
    """
    Comparative jurisdiction analyzer for cross-border legal analysis.
    
    Analyzes legal documents for enforceability, formalities, and tax implications
    across Indian and US jurisdictions, providing recommendations for cross-border
    transactions and compliance strategies.
    """
    
    def __init__(self):
        """Initialize the comparative analyzer with jurisdiction processors."""
        self.indian_processor = IndianLegalProcessor()
        self.us_processor = USLegalProcessor()
        
        # Initialize comparison databases
        self._initialize_enforceability_rules()
        self._initialize_formalities_database()
        self._initialize_tax_treaties()
        self._initialize_governing_law_preferences()
        
    def _initialize_enforceability_rules(self):
        """Initialize enforceability comparison rules."""
        self.enforceability_factors = {
            'contract_formation': {
                'india': {
                    'requirements': ['offer', 'acceptance', 'consideration', 'capacity', 'free consent'],
                    'governing_law': 'Indian Contract Act, 1872',
                    'key_sections': ['Section 10', 'Section 11', 'Section 13']
                },
                'us': {
                    'requirements': ['offer', 'acceptance', 'consideration', 'capacity', 'legality'],
                    'governing_law': 'State contract law (varies by state)',
                    'key_principles': ['Restatement of Contracts', 'UCC for goods']
                }
            },
            'consideration': {
                'india': {
                    'definition': 'Something in return (Section 2(d) Indian Contract Act)',
                    'requirements': ['must be at desire of promisor', 'may move from promisee or third party'],
                    'adequacy': 'Courts generally do not inquire into adequacy'
                },
                'us': {
                    'definition': 'Bargained-for exchange',
                    'requirements': ['legal detriment or benefit', 'bargained-for exchange'],
                    'adequacy': 'Courts do not inquire into adequacy if genuine'
                }
            },
            'remedies': {
                'india': {
                    'damages': 'Section 73 - compensation for loss or damage',
                    'specific_performance': 'Specific Relief Act, 1963',
                    'injunctions': 'Available under Specific Relief Act'
                },
                'us': {
                    'damages': 'Expectation, reliance, restitution damages',
                    'specific_performance': 'Available for unique goods/real estate',
                    'injunctions': 'Available with proper showing'
                }
            }
        }
        
        self.enforceability_risks = {
            'choice_of_law': {
                'india_governing': ['May not enforce foreign penalties', 'Public policy limitations'],
                'us_governing': ['May not recognize Indian stamp duty requirements', 'Conflict with state law'],
                'neutral_law': ['Singapore/English law often preferred', 'International arbitration friendly']
            },
            'dispute_resolution': {
                'indian_courts': ['Enforcement of foreign judgments limited', 'Lengthy proceedings'],
                'us_courts': ['May not have jurisdiction over Indian parties', 'Service of process issues'],
                'arbitration': ['New York Convention applies', 'Generally enforceable in both jurisdictions']
            }
        }
        
    def _initialize_formalities_database(self):
        """Initialize formalities comparison database."""
        self.formalities_comparison = {
            'execution': {
                'india': {
                    'signature_requirements': 'Signatures of parties required',
                    'witness_requirements': 'Two witnesses for certain documents',
                    'notarization': 'Notarization required for some documents',
                    'stamp_duty': 'Mandatory stamp duty based on state and document type'
                },
                'us': {
                    'signature_requirements': 'Signatures required, electronic signatures accepted',
                    'witness_requirements': 'Varies by state and document type',
                    'notarization': 'Required for certain documents (real estate, powers of attorney)',
                    'stamp_duty': 'No stamp duty, but recording fees may apply'
                }
            },
            'registration': {
                'india': {
                    'mandatory_registration': 'Required for documents above certain value',
                    'time_limit': '4 months from execution',
                    'consequences': 'Unregistered documents inadmissible as evidence',
                    'authority': 'Sub-Registrar office'
                },
                'us': {
                    'mandatory_registration': 'Generally not required except for real estate',
                    'time_limit': 'Varies by state',
                    'consequences': 'May affect priority, not validity',
                    'authority': 'County recorder or state agency'
                }
            },
            'stamp_duty': {
                'india': {
                    'applicability': 'All instruments executed in India',
                    'rates': 'Varies by state (0.1% to 8%)',
                    'payment_method': 'Stamp paper or franking',
                    'penalties': 'Up to 10x stamp duty + penalty'
                },
                'us': {
                    'applicability': 'No stamp duty system',
                    'alternatives': 'Recording fees, transfer taxes in some states',
                    'rates': 'Varies by state (if applicable)',
                    'penalties': 'Late fees for recording'
                }
            }
        }
        
    def _initialize_tax_treaties(self):
        """Initialize India-US tax treaty provisions."""
        self.dtaa_provisions = {
            'withholding_tax': {
                'dividends': {
                    'rate': '15% (25% if shareholding < 10%)',
                    'conditions': 'Beneficial ownership required',
                    'exemptions': 'Pension funds, government entities'
                },
                'interest': {
                    'rate': '10% (15% for certain debt instruments)',
                    'conditions': 'Beneficial ownership required',
                    'exemptions': 'Government securities, bank loans'
                },
                'royalties': {
                    'rate': '10% (15% for equipment royalties)',
                    'conditions': 'Beneficial ownership required',
                    'scope': 'Copyright, patent, trademark, technical services'
                },
                'fees_for_technical_services': {
                    'rate': '10%',
                    'conditions': 'Beneficial ownership required',
                    'scope': 'Managerial, technical, consultancy services'
                }
            },
            'business_profits': {
                'permanent_establishment': {
                    'definition': 'Fixed place of business, dependent agent',
                    'threshold': '6 months for construction/installation projects',
                    'exemptions': 'Preparatory/auxiliary activities'
                },
                'taxation': 'Taxable only if PE exists in source country'
            },
            'capital_gains': {
                'shares': 'Taxable in country of residence (with exceptions)',
                'real_estate': 'Taxable in country where property located',
                'business_assets': 'Depends on PE status'
            }
        }
        
        self.transfer_pricing_rules = {
            'india': {
                'threshold': 'INR 1 crore for international transactions',
                'documentation': 'Master file, local file, CbC report',
                'methods': 'CUP, RPM, CPM, PSM, TNMM',
                'penalties': 'Up to 2% of transaction value'
            },
            'us': {
                'threshold': 'Various thresholds based on transaction type',
                'documentation': 'Master file, local file, Forms 8865/5471',
                'methods': 'CUP, RPM, CPM, PSM, unspecified methods',
                'penalties': '20-40% of underpayment'
            }
        }
        
    def _initialize_governing_law_preferences(self):
        """Initialize governing law and dispute resolution preferences."""
        self.governing_law_analysis = {
            'indian_law': {
                'advantages': [
                    'Familiar to Indian parties',
                    'Lower legal costs in India',
                    'Indian courts understand local business practices'
                ],
                'disadvantages': [
                    'May not be enforceable in US without reciprocity',
                    'Stamp duty requirements may be burdensome',
                    'Lengthy court proceedings'
                ],
                'suitable_for': ['India-centric transactions', 'Indian regulatory compliance']
            },
            'us_law': {
                'advantages': [
                    'Well-developed commercial law',
                    'Predictable enforcement',
                    'International business familiarity'
                ],
                'disadvantages': [
                    'May conflict with Indian mandatory laws',
                    'Higher legal costs',
                    'Unfamiliar to Indian parties'
                ],
                'suitable_for': ['US-centric transactions', 'International financing']
            },
            'neutral_law': {
                'options': ['English law', 'Singapore law', 'New York law'],
                'advantages': [
                    'Neutral to both parties',
                    'International arbitration friendly',
                    'Well-developed commercial law'
                ],
                'disadvantages': [
                    'Higher legal costs',
                    'May not address local regulatory issues'
                ],
                'suitable_for': ['Cross-border M&A', 'International joint ventures']
            }
        }
        
        self.dispute_resolution_mechanisms = {
            'litigation': {
                'indian_courts': {
                    'pros': ['Familiar jurisdiction', 'Lower costs', 'Local enforcement'],
                    'cons': ['Lengthy proceedings', 'Limited international enforcement'],
                    'enforcement': 'Difficult to enforce abroad'
                },
                'us_courts': {
                    'pros': ['Efficient proceedings', 'Predictable outcomes', 'International respect'],
                    'cons': ['Higher costs', 'Jurisdictional issues', 'Service of process'],
                    'enforcement': 'Limited enforcement in India'
                }
            },
            'arbitration': {
                'institutional': {
                    'options': ['ICC', 'LCIA', 'SIAC', 'DIAC'],
                    'pros': ['International enforcement', 'Expert arbitrators', 'Confidentiality'],
                    'cons': ['Higher costs', 'Limited appeal rights'],
                    'enforcement': 'New York Convention applies'
                },
                'ad_hoc': {
                    'options': ['UNCITRAL Rules'],
                    'pros': ['Flexibility', 'Lower institutional costs'],
                    'cons': ['Administrative burden', 'Potential delays'],
                    'enforcement': 'New York Convention applies'
                }
            }
        }
    
    def analyze_cross_border_document(
        self, 
        text: str, 
        indian_state: Optional[IndianState] = None,
        us_state: Optional[USState] = None
    ) -> CrossBorderAnalysis:
        """
        Perform comprehensive cross-border analysis of a legal document.
        
        Args:
            text: Document text content
            indian_state: Indian state for jurisdiction-specific analysis
            us_state: US state for jurisdiction-specific analysis
            
        Returns:
            CrossBorderAnalysis with complete comparative analysis
        """
        if not text or not text.strip():
            return self._empty_cross_border_analysis()
        
        # Perform individual jurisdiction analyses
        indian_analysis = self.indian_processor.analyze_document(text, indian_state)
        us_analysis = self.us_processor.analyze_document(text, us_state)
        
        # Perform comparative analyses
        enforceability_comparison = self._compare_enforceability(text, indian_analysis, us_analysis)
        formalities_comparison = self._compare_formalities(text, indian_analysis, us_analysis)
        tax_implications = self._analyze_tax_implications(text, indian_analysis, us_analysis)
        
        # Generate recommendations
        governing_law_recommendation = self._recommend_governing_law(text, indian_analysis, us_analysis)
        dispute_resolution_recommendation = self._recommend_dispute_resolution(text, indian_analysis, us_analysis)
        
        # Identify compliance gaps
        compliance_gaps = self._identify_compliance_gaps(indian_analysis, us_analysis)
        
        # Generate comprehensive recommendations
        recommendations = self._generate_cross_border_recommendations(
            text, indian_analysis, us_analysis, compliance_gaps
        )
        
        # Assess overall risk
        overall_risk = self._assess_overall_cross_border_risk(
            enforceability_comparison, formalities_comparison, tax_implications, compliance_gaps
        )
        
        # Create implementation roadmap
        implementation_roadmap = self._create_implementation_roadmap(recommendations, compliance_gaps)
        
        return CrossBorderAnalysis(
            enforceability_comparison=enforceability_comparison,
            formalities_comparison=formalities_comparison,
            tax_implications=tax_implications,
            recommended_governing_law=governing_law_recommendation,
            recommended_dispute_resolution=dispute_resolution_recommendation,
            compliance_gaps=compliance_gaps,
            recommendations=recommendations,
            overall_risk_assessment=overall_risk,
            implementation_roadmap=implementation_roadmap
        )
    
    def _compare_enforceability(
        self, 
        text: str, 
        indian_analysis: IndianLegalAnalysis, 
        us_analysis: USLegalAnalysis
    ) -> EnforceabilityComparison:
        """Compare enforceability between Indian and US jurisdictions."""
        
        # Analyze Indian enforceability
        india_enforceability = self._analyze_indian_enforceability(text, indian_analysis)
        
        # Analyze US enforceability
        us_enforceability = self._analyze_us_enforceability(text, us_analysis)
        
        # Identify cross-border risks
        cross_border_risks = self._identify_cross_border_enforceability_risks(
            text, indian_analysis, us_analysis
        )
        
        # Calculate enforceability scores
        enforceability_scores = self._calculate_enforceability_scores(
            india_enforceability, us_enforceability, cross_border_risks
        )
        
        # Generate recommendations
        recommendations = self._generate_enforceability_recommendations(
            india_enforceability, us_enforceability, cross_border_risks
        )
        
        # Assess overall risk level
        risk_level = self._assess_enforceability_risk_level(cross_border_risks, enforceability_scores)
        
        return EnforceabilityComparison(
            india_enforceability=india_enforceability,
            us_enforceability=us_enforceability,
            cross_border_risks=cross_border_risks,
            enforceability_score=enforceability_scores,
            recommendations=recommendations,
            risk_level=risk_level
        )
    
    def _compare_formalities(
        self, 
        text: str, 
        indian_analysis: IndianLegalAnalysis, 
        us_analysis: USLegalAnalysis
    ) -> FormalitiesComparison:
        """Compare legal formalities between jurisdictions."""
        
        # Compare stamp duty requirements
        stamp_duty_comparison = self._compare_stamp_duty_requirements(indian_analysis, us_analysis)
        
        # Compare registration requirements
        registration_comparison = self._compare_registration_requirements(indian_analysis, us_analysis)
        
        # Compare witness requirements
        witness_requirements = self._compare_witness_requirements(text)
        
        # Compare notarization requirements
        notarization_requirements = self._compare_notarization_requirements(text)
        
        # Compare execution formalities
        execution_formalities = self._compare_execution_formalities(text)
        
        # Identify compliance gaps
        compliance_gaps = self._identify_formalities_gaps(
            stamp_duty_comparison, registration_comparison, witness_requirements
        )
        
        return FormalitiesComparison(
            stamp_duty_comparison=stamp_duty_comparison,
            registration_comparison=registration_comparison,
            witness_requirements=witness_requirements,
            notarization_requirements=notarization_requirements,
            execution_formalities=execution_formalities,
            compliance_gaps=compliance_gaps
        )
    
    def _analyze_tax_implications(
        self, 
        text: str, 
        indian_analysis: IndianLegalAnalysis, 
        us_analysis: USLegalAnalysis
    ) -> TaxImplications:
        """Analyze tax implications for cross-border transactions."""
        
        # Analyze Indian tax implications
        india_tax_implications = self._analyze_indian_tax_implications(text, indian_analysis)
        
        # Analyze US tax implications
        us_tax_implications = self._analyze_us_tax_implications(text, us_analysis)
        
        # Identify DTAA benefits
        dtaa_benefits = self._identify_dtaa_benefits(text, indian_analysis, us_analysis)
        
        # Analyze withholding tax implications
        withholding_tax = self._analyze_withholding_tax(text, indian_analysis, us_analysis)
        
        # Analyze transfer pricing implications
        transfer_pricing = self._analyze_transfer_pricing_implications(text, indian_analysis, us_analysis)
        
        # Analyze GST implications
        gst_implications = self._analyze_cross_border_gst_implications(text, indian_analysis)
        
        # Generate tax recommendations
        tax_recommendations = self._generate_tax_recommendations(
            india_tax_implications, us_tax_implications, dtaa_benefits, withholding_tax
        )
        
        return TaxImplications(
            india_tax_implications=india_tax_implications,
            us_tax_implications=us_tax_implications,
            dtaa_benefits=dtaa_benefits,
            withholding_tax=withholding_tax,
            transfer_pricing=transfer_pricing,
            gst_implications=gst_implications,
            recommendations=tax_recommendations
        )
    
    def _recommend_governing_law(
        self, 
        text: str, 
        indian_analysis: IndianLegalAnalysis, 
        us_analysis: USLegalAnalysis
    ) -> str:
        """Recommend optimal governing law for the transaction."""
        
        # Analyze transaction characteristics
        transaction_type = self._determine_transaction_type(text)
        parties_location = self._analyze_parties_location(text)
        asset_location = self._analyze_asset_location(text)
        
        # Score different governing law options
        scores = {}
        
        # Score Indian law
        indian_score = self._score_indian_governing_law(
            transaction_type, parties_location, asset_location, indian_analysis
        )
        scores['Indian Law'] = indian_score
        
        # Score US law (state-specific)
        us_score = self._score_us_governing_law(
            transaction_type, parties_location, asset_location, us_analysis
        )
        scores['US Law'] = us_score
        
        # Score neutral laws
        english_score = self._score_english_governing_law(transaction_type, parties_location)
        scores['English Law'] = english_score
        
        singapore_score = self._score_singapore_governing_law(transaction_type, parties_location)
        scores['Singapore Law'] = singapore_score
        
        # Select highest scoring option
        recommended_law = max(scores, key=scores.get)
        
        return f"{recommended_law} (Score: {scores[recommended_law]:.2f})"
    
    def _recommend_dispute_resolution(
        self, 
        text: str, 
        indian_analysis: IndianLegalAnalysis, 
        us_analysis: USLegalAnalysis
    ) -> str:
        """Recommend optimal dispute resolution mechanism."""
        
        # Analyze dispute resolution factors
        transaction_value = self._estimate_transaction_value(text, indian_analysis, us_analysis)
        complexity = self._assess_transaction_complexity(text, indian_analysis, us_analysis)
        confidentiality_needs = self._assess_confidentiality_needs(text)
        enforcement_needs = self._assess_enforcement_needs(text)
        
        # Score different options
        scores = {}
        
        # Score arbitration options
        scores['ICC Arbitration (Paris)'] = self._score_icc_arbitration(
            transaction_value, complexity, confidentiality_needs, enforcement_needs
        )
        scores['SIAC Arbitration (Singapore)'] = self._score_siac_arbitration(
            transaction_value, complexity, confidentiality_needs, enforcement_needs
        )
        scores['LCIA Arbitration (London)'] = self._score_lcia_arbitration(
            transaction_value, complexity, confidentiality_needs, enforcement_needs
        )
        
        # Score litigation options
        scores['Indian Courts'] = self._score_indian_litigation(
            transaction_value, complexity, enforcement_needs
        )
        scores['US Courts'] = self._score_us_litigation(
            transaction_value, complexity, enforcement_needs
        )
        
        # Select highest scoring option
        recommended_mechanism = max(scores, key=scores.get)
        
        return f"{recommended_mechanism} (Score: {scores[recommended_mechanism]:.2f})"
    
    def _identify_compliance_gaps(
        self, 
        indian_analysis: IndianLegalAnalysis, 
        us_analysis: USLegalAnalysis
    ) -> List[JurisdictionComplianceGap]:
        """Identify compliance gaps between jurisdictions."""
        gaps = []
        
        # Formality gaps
        if indian_analysis.stamp_duty.calculated_duty and indian_analysis.stamp_duty.calculated_duty > 0:
            gaps.append(JurisdictionComplianceGap(
                gap_type=ComplianceGap.FORMALITY,
                description="Stamp duty required in India but not in US",
                india_requirement=f"Stamp duty of {indian_analysis.stamp_duty.calculated_duty} required",
                us_requirement="No stamp duty requirement",
                impact="Document may be inadmissible in Indian courts without proper stamp duty",
                mitigation_strategy="Pay stamp duty before document execution or within prescribed time",
                priority="high"
            ))
        
        # Registration gaps
        for reg_req in indian_analysis.registration_requirements:
            if reg_req.required:
                gaps.append(JurisdictionComplianceGap(
                    gap_type=ComplianceGap.REGISTRATION,
                    description="Registration required in India",
                    india_requirement=f"Registration with {reg_req.authority} within {reg_req.time_limit}",
                    us_requirement="Generally no registration required",
                    impact="Unregistered documents inadmissible as evidence in India",
                    mitigation_strategy="Complete registration within prescribed time limit",
                    priority="high"
                ))
        
        # Tax gaps
        if indian_analysis.gst_analysis.applicable:
            gaps.append(JurisdictionComplianceGap(
                gap_type=ComplianceGap.TAX,
                description="GST implications in India",
                india_requirement=f"GST at {indian_analysis.gst_analysis.gst_rate}% may be applicable",
                us_requirement="No GST equivalent (sales tax varies by state)",
                impact="Tax compliance and cost implications",
                mitigation_strategy="Consult tax advisor for GST implications and compliance",
                priority="medium"
            ))
        
        # Governing law gaps
        if us_analysis.state_jurisdiction.choice_of_law_clause:
            gaps.append(JurisdictionComplianceGap(
                gap_type=ComplianceGap.GOVERNING_LAW,
                description="Choice of law clause may conflict with Indian mandatory laws",
                india_requirement="Indian mandatory laws cannot be contracted out",
                us_requirement="Party autonomy in choice of law generally respected",
                impact="Potential unenforceability of certain provisions in India",
                mitigation_strategy="Include carve-out for Indian mandatory laws",
                priority="medium"
            ))
        
        return gaps
    
    def _generate_cross_border_recommendations(
        self, 
        text: str, 
        indian_analysis: IndianLegalAnalysis, 
        us_analysis: USLegalAnalysis,
        compliance_gaps: List[JurisdictionComplianceGap]
    ) -> List[CrossBorderRecommendation]:
        """Generate comprehensive cross-border recommendations."""
        recommendations = []
        
        # Governing law recommendation
        recommendations.append(CrossBorderRecommendation(
            category="Governing Law",
            priority="high",
            description="Consider neutral governing law for cross-border enforceability",
            rationale="Reduces jurisdictional bias and improves enforceability in both countries",
            implementation_steps=[
                "Evaluate transaction characteristics",
                "Consider English or Singapore law",
                "Include carve-out for mandatory local laws",
                "Ensure legal opinions from both jurisdictions"
            ],
            estimated_cost="$10,000 - $25,000 for legal opinions",
            timeline="2-4 weeks"
        ))
        
        # Dispute resolution recommendation
        recommendations.append(CrossBorderRecommendation(
            category="Dispute Resolution",
            priority="high",
            description="Use international arbitration for cross-border disputes",
            rationale="Better enforceability under New York Convention",
            implementation_steps=[
                "Select appropriate arbitration institution (ICC/SIAC/LCIA)",
                "Choose neutral seat of arbitration",
                "Specify arbitration rules and procedures",
                "Include expedited procedures for smaller disputes"
            ],
            estimated_cost="$50,000 - $200,000 per arbitration",
            timeline="12-18 months typical duration"
        ))
        
        # Tax optimization recommendation
        if any(gap.gap_type == ComplianceGap.TAX for gap in compliance_gaps):
            recommendations.append(CrossBorderRecommendation(
                category="Tax Optimization",
                priority="medium",
                description="Structure transaction to optimize tax efficiency",
                rationale="Minimize withholding taxes and utilize DTAA benefits",
                implementation_steps=[
                    "Obtain tax residency certificates",
                    "Structure payments to qualify for DTAA benefits",
                    "Consider timing of payments",
                    "Implement transfer pricing documentation"
                ],
                estimated_cost="$15,000 - $50,000 for tax structuring",
                timeline="4-8 weeks"
            ))
        
        # Compliance recommendation
        if compliance_gaps:
            recommendations.append(CrossBorderRecommendation(
                category="Compliance",
                priority="high",
                description="Address jurisdiction-specific compliance requirements",
                rationale="Ensure enforceability and avoid penalties in both jurisdictions",
                implementation_steps=[
                    "Complete Indian stamp duty and registration requirements",
                    "Ensure US state law compliance",
                    "Implement ongoing compliance monitoring",
                    "Establish local legal counsel relationships"
                ],
                estimated_cost="$5,000 - $20,000 for compliance setup",
                timeline="2-6 weeks"
            ))
        
        return recommendations
    
    # Helper methods for detailed analysis
    
    def _empty_cross_border_analysis(self) -> CrossBorderAnalysis:
        """Return empty cross-border analysis for invalid input."""
        return CrossBorderAnalysis(
            enforceability_comparison=EnforceabilityComparison(
                india_enforceability={},
                us_enforceability={},
                cross_border_risks=[],
                enforceability_score={'india': 0.0, 'us': 0.0},
                recommendations=[],
                risk_level=EnforceabilityRisk.CRITICAL
            ),
            formalities_comparison=FormalitiesComparison(
                stamp_duty_comparison={},
                registration_comparison={},
                witness_requirements={},
                notarization_requirements={},
                execution_formalities={},
                compliance_gaps=[]
            ),
            tax_implications=TaxImplications(
                india_tax_implications={},
                us_tax_implications={},
                dtaa_benefits=[],
                withholding_tax={},
                transfer_pricing={},
                gst_implications={},
                recommendations=[]
            ),
            recommended_governing_law="Unable to determine",
            recommended_dispute_resolution="Unable to determine",
            compliance_gaps=[],
            recommendations=[],
            overall_risk_assessment="critical",
            implementation_roadmap=[]
        )
    
    def _analyze_indian_enforceability(self, text: str, analysis: IndianLegalAnalysis) -> Dict[str, Any]:
        """Analyze enforceability under Indian law."""
        return {
            'contract_validity': self._assess_indian_contract_validity(text, analysis),
            'mandatory_compliance': self._assess_indian_mandatory_compliance(analysis),
            'enforcement_mechanisms': self._assess_indian_enforcement_mechanisms(text),
            'potential_challenges': self._identify_indian_enforcement_challenges(text, analysis),
            'enforceability_score': self._calculate_indian_enforceability_score(text, analysis)
        }
    
    def _analyze_us_enforceability(self, text: str, analysis: USLegalAnalysis) -> Dict[str, Any]:
        """Analyze enforceability under US law."""
        return {
            'contract_validity': self._assess_us_contract_validity(text, analysis),
            'state_law_compliance': self._assess_us_state_compliance(analysis),
            'enforcement_mechanisms': self._assess_us_enforcement_mechanisms(text),
            'potential_challenges': self._identify_us_enforcement_challenges(text, analysis),
            'enforceability_score': self._calculate_us_enforceability_score(text, analysis)
        }
    
    def _assess_overall_cross_border_risk(
        self, 
        enforceability: EnforceabilityComparison,
        formalities: FormalitiesComparison,
        tax: TaxImplications,
        gaps: List[JurisdictionComplianceGap]
    ) -> str:
        """Assess overall cross-border risk level."""
        
        # Calculate risk factors
        enforceability_risk = 1.0 if enforceability.risk_level == EnforceabilityRisk.CRITICAL else 0.5
        formalities_risk = len(formalities.compliance_gaps) * 0.1
        tax_risk = len(tax.recommendations) * 0.1
        compliance_risk = len([g for g in gaps if g.priority == "high"]) * 0.2
        
        total_risk = enforceability_risk + formalities_risk + tax_risk + compliance_risk
        
        if total_risk >= 1.5:
            return "critical"
        elif total_risk >= 1.0:
            return "high"
        elif total_risk >= 0.5:
            return "medium"
        else:
            return "low"
    
    def _create_implementation_roadmap(
        self, 
        recommendations: List[CrossBorderRecommendation],
        gaps: List[JurisdictionComplianceGap]
    ) -> List[str]:
        """Create implementation roadmap based on recommendations and gaps."""
        
        roadmap = []
        
        # Phase 1: Critical compliance items
        high_priority_items = [r for r in recommendations if r.priority == "high"]
        if high_priority_items:
            roadmap.append("Phase 1 (Weeks 1-2): Address critical compliance requirements")
            for item in high_priority_items:
                roadmap.extend([f"  - {step}" for step in item.implementation_steps[:2]])
        
        # Phase 2: Legal structure optimization
        roadmap.append("Phase 2 (Weeks 3-4): Optimize legal structure")
        roadmap.extend([
            "  - Finalize governing law selection",
            "  - Draft dispute resolution clauses",
            "  - Complete legal due diligence"
        ])
        
        # Phase 3: Tax and regulatory compliance
        roadmap.append("Phase 3 (Weeks 5-6): Tax and regulatory setup")
        roadmap.extend([
            "  - Implement tax optimization strategies",
            "  - Complete regulatory filings",
            "  - Establish ongoing compliance procedures"
        ])
        
        # Phase 4: Documentation and execution
        roadmap.append("Phase 4 (Weeks 7-8): Documentation and execution")
        roadmap.extend([
            "  - Finalize transaction documentation",
            "  - Complete execution formalities",
            "  - Implement post-closing compliance"
        ])
        
        return roadmap
    
    # Helper methods for detailed analysis
    
    def _assess_indian_contract_validity(self, text: str, analysis: IndianLegalAnalysis) -> Dict[str, Any]:
        """Assess contract validity under Indian Contract Act."""
        return {
            'essential_elements': 'Present' if analysis.compliance_check.compliant else 'Missing elements',
            'consideration': 'Valid' if analysis.monetary_amounts else 'Needs verification',
            'capacity': 'Assumed valid',
            'free_consent': 'Needs verification',
            'lawful_object': 'Assumed lawful'
        }
    
    def _assess_us_contract_validity(self, text: str, analysis: USLegalAnalysis) -> Dict[str, Any]:
        """Assess contract validity under US law."""
        return {
            'essential_elements': 'Present' if analysis.compliance_check.compliant else 'Missing elements',
            'consideration': 'Valid' if analysis.monetary_amounts else 'Needs verification',
            'capacity': 'Assumed valid',
            'legality': 'Assumed legal',
            'statute_of_frauds': 'Needs verification for certain contracts'
        }
    
    def _calculate_indian_enforceability_score(self, text: str, analysis: IndianLegalAnalysis) -> float:
        """Calculate enforceability score for Indian jurisdiction."""
        score = 0.5  # Base score
        
        if analysis.compliance_check.compliant:
            score += 0.3
        if analysis.stamp_duty.compliance_status == 'compliant':
            score += 0.2
        if analysis.registration_requirements and all(not req.required for req in analysis.registration_requirements):
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_us_enforceability_score(self, text: str, analysis: USLegalAnalysis) -> float:
        """Calculate enforceability score for US jurisdiction."""
        score = 0.6  # Base score (generally higher due to developed legal system)
        
        if analysis.compliance_check.compliant:
            score += 0.3
        if analysis.state_jurisdiction.governing_state:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_indian_mandatory_compliance(self, analysis: IndianLegalAnalysis) -> Dict[str, Any]:
        """Assess Indian mandatory law compliance."""
        return {
            'stamp_duty_compliance': analysis.stamp_duty.compliance_status,
            'registration_compliance': 'required' if any(req.required for req in analysis.registration_requirements) else 'not_required',
            'gst_compliance': 'applicable' if analysis.gst_analysis.applicable else 'not_applicable',
            'act_compliance': 'compliant' if analysis.compliance_check.compliant else 'non_compliant'
        }
    
    def _assess_indian_enforcement_mechanisms(self, text: str) -> List[str]:
        """Assess available enforcement mechanisms in India."""
        return [
            'Civil courts under CPC',
            'Specific performance under Specific Relief Act',
            'Arbitration under Arbitration Act 2015',
            'Consumer forums (if applicable)',
            'Company Law Tribunal (for corporate matters)'
        ]
    
    def _assess_us_state_compliance(self, analysis: USLegalAnalysis) -> Dict[str, Any]:
        """Assess US state law compliance."""
        return {
            'governing_state': analysis.state_jurisdiction.governing_state.value if analysis.state_jurisdiction.governing_state else 'Unknown',
            'choice_of_law': analysis.state_jurisdiction.choice_of_law_clause,
            'forum_selection': analysis.state_jurisdiction.forum_selection_clause,
            'state_requirements': analysis.state_jurisdiction.state_specific_requirements,
            'conflicts': analysis.state_jurisdiction.conflicts_of_law
        }
    
    def _assess_us_enforcement_mechanisms(self, text: str) -> List[str]:
        """Assess available enforcement mechanisms in US."""
        return [
            'Federal and state courts',
            'Specific performance (limited availability)',
            'Arbitration under FAA',
            'Administrative agencies (if applicable)',
            'Bankruptcy courts (if applicable)'
        ]
    
    def _identify_indian_enforcement_challenges(self, text: str, analysis: IndianLegalAnalysis) -> List[str]:
        """Identify potential enforcement challenges in India."""
        challenges = []
        
        if analysis.stamp_duty.compliance_status != 'compliant':
            challenges.append('Unstamped documents inadmissible as evidence')
        
        if any(req.required for req in analysis.registration_requirements):
            challenges.append('Unregistered documents may not be admissible')
        
        if 'foreign' in text.lower() or 'international' in text.lower():
            challenges.append('Foreign exchange regulations may apply')
        
        challenges.extend([
            'Lengthy court proceedings',
            'Enforcement of foreign judgments limited',
            'Service of process on foreign parties'
        ])
        
        return challenges
    
    def _identify_us_enforcement_challenges(self, text: str, analysis: USLegalAnalysis) -> List[str]:
        """Identify potential enforcement challenges in US."""
        challenges = []
        
        if analysis.state_jurisdiction.conflicts_of_law:
            challenges.extend(analysis.state_jurisdiction.conflicts_of_law)
        
        if 'indian' in text.lower() or 'india' in text.lower():
            challenges.append('Service of process in India may be challenging')
            challenges.append('Enforcement in India requires separate proceedings')
        
        challenges.extend([
            'Jurisdictional challenges for foreign parties',
            'Choice of law conflicts',
            'Discovery limitations for foreign entities'
        ])
        
        return challenges
    
    def _identify_cross_border_enforceability_risks(
        self, 
        text: str, 
        indian_analysis: IndianLegalAnalysis, 
        us_analysis: USLegalAnalysis
    ) -> List[str]:
        """Identify cross-border enforceability risks."""
        risks = []
        
        # Stamp duty risks
        if indian_analysis.stamp_duty.compliance_status != 'compliant':
            risks.append('Unstamped documents may not be enforceable in Indian courts')
        
        # Registration risks
        if any(req.required for req in indian_analysis.registration_requirements):
            risks.append('Unregistered documents may face enforceability issues in India')
        
        # Choice of law risks
        if us_analysis.state_jurisdiction.choice_of_law_clause:
            risks.append('US governing law may conflict with Indian mandatory provisions')
        
        # Service of process risks
        risks.append('Service of process across borders may be challenging')
        risks.append('Enforcement of judgments requires separate proceedings in each jurisdiction')
        
        # Currency and exchange control risks
        if indian_analysis.monetary_amounts or us_analysis.monetary_amounts:
            risks.append('Foreign exchange regulations may affect payment enforcement')
        
        return risks
    
    def _calculate_enforceability_scores(
        self, 
        india_enforceability: Dict[str, Any], 
        us_enforceability: Dict[str, Any], 
        cross_border_risks: List[str]
    ) -> Dict[str, float]:
        """Calculate enforceability scores for both jurisdictions."""
        
        # Base scores
        india_score = india_enforceability.get('enforceability_score', 0.5)
        us_score = us_enforceability.get('enforceability_score', 0.6)
        
        # Adjust for cross-border risks
        risk_penalty = len(cross_border_risks) * 0.05
        
        india_score = max(0.0, india_score - risk_penalty)
        us_score = max(0.0, us_score - risk_penalty)
        
        return {
            'india': india_score,
            'us': us_score
        }
    
    def _generate_enforceability_recommendations(
        self, 
        india_enforceability: Dict[str, Any], 
        us_enforceability: Dict[str, Any], 
        cross_border_risks: List[str]
    ) -> List[str]:
        """Generate enforceability recommendations."""
        recommendations = []
        
        # Address stamp duty issues
        if 'stamp duty' in str(cross_border_risks).lower():
            recommendations.append('Ensure proper stamp duty compliance in India before execution')
        
        # Address registration issues
        if 'registration' in str(cross_border_risks).lower():
            recommendations.append('Complete document registration within prescribed time limits')
        
        # Address choice of law issues
        if 'governing law' in str(cross_border_risks).lower():
            recommendations.append('Include carve-out for mandatory local laws in choice of law clause')
        
        # General recommendations
        recommendations.extend([
            'Consider neutral governing law for better cross-border enforceability',
            'Use international arbitration for dispute resolution',
            'Obtain legal opinions from both jurisdictions',
            'Include specific enforcement mechanisms in the agreement'
        ])
        
        return recommendations
    
    def _assess_enforceability_risk_level(
        self, 
        cross_border_risks: List[str], 
        enforceability_scores: Dict[str, float]
    ) -> EnforceabilityRisk:
        """Assess overall enforceability risk level."""
        
        avg_score = (enforceability_scores['india'] + enforceability_scores['us']) / 2
        risk_count = len(cross_border_risks)
        
        if avg_score < 0.3 or risk_count >= 6:
            return EnforceabilityRisk.CRITICAL
        elif avg_score < 0.5 or risk_count >= 4:
            return EnforceabilityRisk.HIGH
        elif avg_score < 0.7 or risk_count >= 2:
            return EnforceabilityRisk.MEDIUM
        else:
            return EnforceabilityRisk.LOW
    
    def _compare_stamp_duty_requirements(self, indian_analysis: IndianLegalAnalysis, us_analysis: USLegalAnalysis) -> Dict[str, Any]:
        """Compare stamp duty requirements between jurisdictions."""
        return {
            'india': {
                'required': True,
                'rate': indian_analysis.stamp_duty.stamp_duty_rate,
                'amount': float(indian_analysis.stamp_duty.calculated_duty) if indian_analysis.stamp_duty.calculated_duty else 0,
                'compliance_status': indian_analysis.stamp_duty.compliance_status
            },
            'us': {
                'required': False,
                'rate': 0,
                'amount': 0,
                'compliance_status': 'not_applicable'
            },
            'gap_analysis': 'India requires stamp duty while US does not - creates compliance burden'
        }
    
    def _compare_registration_requirements(self, indian_analysis: IndianLegalAnalysis, us_analysis: USLegalAnalysis) -> Dict[str, Any]:
        """Compare registration requirements between jurisdictions."""
        indian_reg_required = any(req.required for req in indian_analysis.registration_requirements)
        
        return {
            'india': {
                'required': indian_reg_required,
                'authority': 'Sub-Registrar' if indian_reg_required else 'N/A',
                'time_limit': '4 months' if indian_reg_required else 'N/A'
            },
            'us': {
                'required': False,
                'authority': 'N/A',
                'time_limit': 'N/A'
            },
            'gap_analysis': 'India may require registration while US generally does not'
        }
    
    def _compare_witness_requirements(self, text: str) -> Dict[str, Any]:
        """Compare witness requirements between jurisdictions."""
        return {
            'india': {
                'required': 'Two witnesses for certain documents',
                'attestation': 'Required for some document types'
            },
            'us': {
                'required': 'Varies by state and document type',
                'attestation': 'Notarization may be required'
            },
            'gap_analysis': 'Different witness and attestation requirements'
        }
    
    def _compare_notarization_requirements(self, text: str) -> Dict[str, Any]:
        """Compare notarization requirements between jurisdictions."""
        return {
            'india': {
                'required': 'For certain documents',
                'authority': 'Notary Public'
            },
            'us': {
                'required': 'For certain documents (varies by state)',
                'authority': 'Notary Public or Commissioner of Oaths'
            },
            'gap_analysis': 'Similar notarization systems but different requirements'
        }
    
    def _compare_execution_formalities(self, text: str) -> Dict[str, Any]:
        """Compare execution formalities between jurisdictions."""
        return {
            'india': {
                'signature_requirements': 'Physical signatures preferred',
                'electronic_signatures': 'Accepted under IT Act 2000',
                'execution_date': 'Must be clearly mentioned'
            },
            'us': {
                'signature_requirements': 'Physical or electronic signatures',
                'electronic_signatures': 'Widely accepted under ESIGN Act',
                'execution_date': 'Must be clearly mentioned'
            },
            'gap_analysis': 'Both jurisdictions accept electronic signatures with different frameworks'
        }
    
    def _identify_formalities_gaps(self, stamp_duty: Dict[str, Any], registration: Dict[str, Any], witness: Dict[str, Any]) -> List[str]:
        """Identify formalities compliance gaps."""
        gaps = []
        
        if stamp_duty['india']['required'] and not stamp_duty['us']['required']:
            gaps.append('Stamp duty required in India but not in US')
        
        if registration['india']['required'] and not registration['us']['required']:
            gaps.append('Registration required in India but not in US')
        
        gaps.append('Different witness and notarization requirements')
        gaps.append('Different execution formality standards')
        
        return gaps
    
    def _analyze_indian_tax_implications(self, text: str, analysis: IndianLegalAnalysis) -> Dict[str, Any]:
        """Analyze Indian tax implications."""
        return {
            'gst_applicable': analysis.gst_analysis.applicable,
            'gst_rate': analysis.gst_analysis.gst_rate,
            'withholding_tax': 'May apply on payments to non-residents',
            'income_tax': 'Applicable on Indian source income',
            'transfer_pricing': 'Applicable for international transactions > INR 1 crore'
        }
    
    def _analyze_us_tax_implications(self, text: str, analysis: USLegalAnalysis) -> Dict[str, Any]:
        """Analyze US tax implications."""
        return {
            'federal_tax': 'Applicable on US source income',
            'state_tax': f'Varies by state ({analysis.state_jurisdiction.governing_state.value if analysis.state_jurisdiction.governing_state else "Unknown"})',
            'withholding_tax': 'May apply on payments to non-residents',
            'transfer_pricing': 'Applicable for related party transactions'
        }
    
    def _identify_dtaa_benefits(self, text: str, indian_analysis: IndianLegalAnalysis, us_analysis: USLegalAnalysis) -> List[str]:
        """Identify DTAA benefits available."""
        benefits = []
        
        if 'royalty' in text.lower() or 'royalties' in text.lower():
            benefits.append('Reduced withholding tax on royalties (10-15%)')
        
        if 'interest' in text.lower():
            benefits.append('Reduced withholding tax on interest (10-15%)')
        
        if 'dividend' in text.lower():
            benefits.append('Reduced withholding tax on dividends (15-25%)')
        
        if 'technical' in text.lower() or 'consulting' in text.lower():
            benefits.append('Reduced withholding tax on fees for technical services (10%)')
        
        benefits.extend([
            'Mutual agreement procedure for dispute resolution',
            'Exchange of information between tax authorities',
            'Tie-breaker rules for tax residency'
        ])
        
        return benefits
    
    def _analyze_withholding_tax(self, text: str, indian_analysis: IndianLegalAnalysis, us_analysis: USLegalAnalysis) -> Dict[str, Any]:
        """Analyze withholding tax implications."""
        return {
            'india_to_us': {
                'applicable': True,
                'rates': self.dtaa_provisions['withholding_tax'],
                'compliance': 'TDS certificate and Form 10F required'
            },
            'us_to_india': {
                'applicable': True,
                'rates': 'Generally 30% unless DTAA applies',
                'compliance': 'Form W-8BEN required for treaty benefits'
            },
            'recommendations': [
                'Obtain tax residency certificates',
                'File appropriate forms for treaty benefits',
                'Consider timing of payments for optimal rates'
            ]
        }
    
    def _analyze_transfer_pricing_implications(self, text: str, indian_analysis: IndianLegalAnalysis, us_analysis: USLegalAnalysis) -> Dict[str, Any]:
        """Analyze transfer pricing implications."""
        return {
            'india_requirements': self.transfer_pricing_rules['india'],
            'us_requirements': self.transfer_pricing_rules['us'],
            'documentation_needed': [
                'Master file and local file',
                'Economic analysis of pricing',
                'Benchmarking study',
                'Board resolutions'
            ],
            'compliance_timeline': 'Annual documentation and filing requirements'
        }
    
    def _analyze_cross_border_gst_implications(self, text: str, analysis: IndianLegalAnalysis) -> Dict[str, Any]:
        """Analyze GST implications for cross-border transactions."""
        return {
            'applicable': analysis.gst_analysis.applicable,
            'rate': analysis.gst_analysis.gst_rate,
            'place_of_supply': analysis.gst_analysis.place_of_supply,
            'reverse_charge': analysis.gst_analysis.reverse_charge,
            'export_implications': 'Zero-rated supplies if export conditions met',
            'import_implications': 'IGST applicable on import of services'
        }
    
    def _generate_tax_recommendations(self, india_tax: Dict[str, Any], us_tax: Dict[str, Any], dtaa_benefits: List[str], withholding_tax: Dict[str, Any]) -> List[str]:
        """Generate tax optimization recommendations."""
        recommendations = []
        
        if dtaa_benefits:
            recommendations.append('Utilize India-US DTAA benefits to minimize withholding taxes')
        
        if india_tax.get('gst_applicable'):
            recommendations.append('Structure services to optimize GST implications')
        
        recommendations.extend([
            'Obtain advance pricing agreements for transfer pricing certainty',
            'Consider tax-efficient payment structures',
            'Implement proper documentation for treaty benefits',
            'Regular compliance monitoring for both jurisdictions'
        ])
        
        return recommendations
    
    def _determine_transaction_type(self, text: str) -> str:
        """Determine the type of transaction from document text."""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['software', 'development', 'it services']):
            return 'software_services'
        elif any(term in text_lower for term in ['consulting', 'advisory', 'professional services']):
            return 'consulting_services'
        elif any(term in text_lower for term in ['sale', 'purchase', 'goods']):
            return 'sale_of_goods'
        elif any(term in text_lower for term in ['loan', 'credit', 'financing']):
            return 'financing'
        elif any(term in text_lower for term in ['joint venture', 'partnership']):
            return 'joint_venture'
        else:
            return 'general_commercial'
    
    def _analyze_parties_location(self, text: str) -> Dict[str, str]:
        """Analyze the location of parties from document text."""
        locations = {}
        
        if 'delaware' in text.lower():
            locations['us_party'] = 'Delaware'
        elif 'new york' in text.lower():
            locations['us_party'] = 'New York'
        elif 'california' in text.lower():
            locations['us_party'] = 'California'
        
        if 'india' in text.lower() or 'indian' in text.lower():
            locations['indian_party'] = 'India'
        
        return locations
    
    def _analyze_asset_location(self, text: str) -> Dict[str, str]:
        """Analyze the location of assets from document text."""
        assets = {}
        
        if 'intellectual property' in text.lower() or 'ip' in text.lower():
            assets['ip_location'] = 'To be determined based on registration'
        
        if 'software' in text.lower():
            assets['software_location'] = 'Cloud/distributed'
        
        return assets
    
    def _score_indian_governing_law(self, transaction_type: str, parties: Dict[str, str], assets: Dict[str, str], analysis: IndianLegalAnalysis) -> float:
        """Score Indian governing law option."""
        score = 0.3  # Base score
        
        if 'indian_party' in parties:
            score += 0.3
        
        if analysis.compliance_check.compliant:
            score += 0.2
        
        if transaction_type in ['software_services', 'consulting_services']:
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_us_governing_law(self, transaction_type: str, parties: Dict[str, str], assets: Dict[str, str], analysis: USLegalAnalysis) -> float:
        """Score US governing law option."""
        score = 0.4  # Base score (higher due to developed legal system)
        
        if 'us_party' in parties:
            score += 0.3
        
        if analysis.compliance_check.compliant:
            score += 0.2
        
        if transaction_type in ['financing', 'joint_venture']:
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_english_governing_law(self, transaction_type: str, parties: Dict[str, str]) -> float:
        """Score English governing law option."""
        score = 0.6  # Base score (neutral and well-developed)
        
        if len(parties) >= 2:  # Cross-border transaction
            score += 0.2
        
        if transaction_type in ['joint_venture', 'financing']:
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_singapore_governing_law(self, transaction_type: str, parties: Dict[str, str]) -> float:
        """Score Singapore governing law option."""
        score = 0.65  # Base score (neutral, Asia-friendly)
        
        if 'indian_party' in parties and 'us_party' in parties:
            score += 0.2
        
        if transaction_type in ['software_services', 'consulting_services']:
            score += 0.1
        
        return min(score, 1.0)
    
    def _estimate_transaction_value(self, text: str, indian_analysis: IndianLegalAnalysis, us_analysis: USLegalAnalysis) -> float:
        """Estimate transaction value from document and analyses."""
        # Try to extract from Indian analysis first
        if indian_analysis.monetary_amounts:
            return float(indian_analysis.monetary_amounts[0].amount)
        
        # Try to extract from US analysis
        if us_analysis.monetary_amounts:
            return float(us_analysis.monetary_amounts[0].amount)
        
        # Try to extract from text directly
        import re
        amount_patterns = [
            r'\$\s*([\d,]+(?:\.\d{2})?)',
            r'([\d,]+(?:\.\d{2})?)\s*(?:usd|dollars?)',
            r'rs\.?\s*([\d,]+(?:\.\d{2})?)',
            r'([\d,]+(?:\.\d{2})?)\s*(?:rs\.?|rupees?)'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    amount_str = matches[0].replace(',', '')
                    return float(amount_str)
                except ValueError:
                    continue
        
        return 100000.0  # Default estimate
    
    def _assess_transaction_complexity(self, text: str, indian_analysis: IndianLegalAnalysis, us_analysis: USLegalAnalysis) -> str:
        """Assess transaction complexity level."""
        complexity_factors = 0
        
        # Check for multiple jurisdictions
        if 'india' in text.lower() and ('us' in text.lower() or 'united states' in text.lower()):
            complexity_factors += 1
        
        # Check for IP involved
        if 'intellectual property' in text.lower() or 'patent' in text.lower() or 'copyright' in text.lower():
            complexity_factors += 1
        
        # Check for regulatory compliance
        if indian_analysis.gst_analysis.applicable or us_analysis.securities_analysis.securities_involved:
            complexity_factors += 1
        
        # Check for multiple parties
        if text.count('party') > 2 or text.count('company') > 2:
            complexity_factors += 1
        
        if complexity_factors >= 3:
            return 'high'
        elif complexity_factors >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _assess_confidentiality_needs(self, text: str) -> str:
        """Assess confidentiality requirements."""
        if 'confidential' in text.lower() or 'proprietary' in text.lower() or 'trade secret' in text.lower():
            return 'high'
        elif 'non-disclosure' in text.lower() or 'nda' in text.lower():
            return 'medium'
        else:
            return 'low'
    
    def _assess_enforcement_needs(self, text: str) -> str:
        """Assess enforcement requirements."""
        if 'international' in text.lower() and ('enforcement' in text.lower() or 'judgment' in text.lower()):
            return 'high'
        elif any(term in text.lower() for term in ['cross-border', 'foreign', 'overseas']):
            return 'medium'
        else:
            return 'low'
    
    def _score_icc_arbitration(self, value: float, complexity: str, confidentiality: str, enforcement: str) -> float:
        """Score ICC arbitration option."""
        score = 0.7  # Base score
        
        if value > 1000000:  # High value transactions
            score += 0.1
        if complexity == 'high':
            score += 0.1
        if enforcement == 'high':
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_siac_arbitration(self, value: float, complexity: str, confidentiality: str, enforcement: str) -> float:
        """Score SIAC arbitration option."""
        score = 0.75  # Base score (Asia-friendly)
        
        if value > 500000:
            score += 0.1
        if complexity in ['medium', 'high']:
            score += 0.1
        if enforcement == 'high':
            score += 0.05
        
        return min(score, 1.0)
    
    def _score_lcia_arbitration(self, value: float, complexity: str, confidentiality: str, enforcement: str) -> float:
        """Score LCIA arbitration option."""
        score = 0.65  # Base score
        
        if value > 2000000:  # Very high value
            score += 0.15
        if complexity == 'high':
            score += 0.1
        if confidentiality == 'high':
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_indian_litigation(self, value: float, complexity: str, enforcement: str) -> float:
        """Score Indian litigation option."""
        score = 0.4  # Base score
        
        if value < 100000:  # Lower value transactions
            score += 0.2
        if complexity == 'low':
            score += 0.1
        if enforcement == 'low':
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_us_litigation(self, value: float, complexity: str, enforcement: str) -> float:
        """Score US litigation option."""
        score = 0.5  # Base score
        
        if value < 500000:
            score += 0.1
        if complexity == 'low':
            score += 0.1
        if enforcement in ['low', 'medium']:
            score += 0.1
        
        return min(score, 1.0)