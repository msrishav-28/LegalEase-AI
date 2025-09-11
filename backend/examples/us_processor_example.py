"""
Example usage of US legal system processor.

Demonstrates USC and CFR citation extraction, UCC applicability detection,
state law jurisdiction detection, and securities and privacy law compliance verification.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.jurisdiction.us_processor import USLegalProcessor, USState


def print_separator(title: str):
    """Print a formatted separator."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_analysis_results(analysis, title: str):
    """Print formatted analysis results."""
    print_separator(title)
    
    print(f"\n📋 Federal Law References ({len(analysis.federal_references)}):")
    for ref in analysis.federal_references:
        print(f"  • {ref.law_name}")
        if ref.sections:
            print(f"    Sections: {', '.join(ref.sections)}")
        print(f"    Confidence: {ref.confidence:.2f}")
        if ref.citation:
            print(f"    Citation: {ref.citation}")
    
    print(f"\n🏛️ State Jurisdiction Analysis:")
    if analysis.state_jurisdiction.governing_state:
        print(f"  • Governing State: {analysis.state_jurisdiction.governing_state.value}")
    if analysis.state_jurisdiction.choice_of_law_clause:
        print(f"  • Choice of Law: {analysis.state_jurisdiction.choice_of_law_clause[:100]}...")
    if analysis.state_jurisdiction.forum_selection_clause:
        print(f"  • Forum Selection: {analysis.state_jurisdiction.forum_selection_clause[:100]}...")
    
    print(f"\n📜 UCC Analysis:")
    print(f"  • Applicable: {analysis.ucc_analysis.applicable}")
    if analysis.ucc_analysis.applicable:
        print(f"  • Articles: {', '.join(analysis.ucc_analysis.articles)}")
        if analysis.ucc_analysis.transaction_type:
            print(f"  • Transaction Type: {analysis.ucc_analysis.transaction_type}")
        if analysis.ucc_analysis.compliance_requirements:
            print(f"  • Requirements: {len(analysis.ucc_analysis.compliance_requirements)} items")
    
    print(f"\n🏦 Securities Analysis:")
    print(f"  • Securities Involved: {analysis.securities_analysis.securities_involved}")
    if analysis.securities_analysis.securities_involved:
        print(f"  • Federal Exemptions: {', '.join(analysis.securities_analysis.federal_exemptions)}")
        print(f"  • Compliance Status: {analysis.securities_analysis.compliance_status}")
        print(f"  • Risk Level: {analysis.securities_analysis.risk_level}")
    
    print(f"\n🔒 Privacy Analysis:")
    if analysis.privacy_analysis.applicable_laws:
        print(f"  • Applicable Laws: {', '.join(analysis.privacy_analysis.applicable_laws)}")
        print(f"  • Data Types: {len(analysis.privacy_analysis.data_types_processed)} identified")
        print(f"  • Compliance Gaps: {len(analysis.privacy_analysis.compliance_gaps)} found")
    else:
        print(f"  • No privacy laws detected")
    
    print(f"\n💰 Monetary Amounts ({len(analysis.monetary_amounts)}):")
    for amount in analysis.monetary_amounts[:5]:  # Show top 5
        print(f"  • {amount.formatted_amount} ({amount.original_text})")
    
    print(f"\n✅ Compliance Check:")
    print(f"  • Compliant: {analysis.compliance_check.compliant}")
    print(f"  • Risk Level: {analysis.compliance_check.risk_level}")
    print(f"  • Missing Clauses: {len(analysis.compliance_check.missing_clauses)}")
    print(f"  • Violations: {len(analysis.compliance_check.violations)}")
    
    print(f"\n📝 Jurisdiction Notes:")
    for note in analysis.jurisdiction_specific_notes:
        print(f"  • {note}")


def example_securities_agreement():
    """Example: Securities Purchase Agreement."""
    text = """
    SECURITIES PURCHASE AGREEMENT
    
    This Securities Purchase Agreement (this "Agreement") is entered into as of [Date], 
    between [Company Name], a Delaware corporation (the "Company"), and the investors 
    listed on Schedule A hereto (each, an "Investor" and collectively, the "Investors").
    
    RECITALS
    
    WHEREAS, the Company desires to issue and sell to the Investors, and the Investors 
    desire to purchase from the Company, shares of the Company's Series A Preferred Stock 
    (the "Shares") for an aggregate purchase price of $5,000,000;
    
    WHEREAS, the sale of the Shares has not been registered under the Securities Act of 1933, 
    as amended (the "Securities Act"), and is being made in reliance upon the exemption 
    from registration provided by Rule 506(b) of Regulation D promulgated under the Securities Act;
    
    WHEREAS, each Investor represents that it is an "accredited investor" as defined in 
    Rule 501 of Regulation D;
    
    NOW, THEREFORE, in consideration of the mutual covenants and agreements contained herein, 
    the parties agree as follows:
    
    1. PURCHASE AND SALE OF SHARES
    The Company agrees to issue and sell to each Investor, and each Investor agrees to 
    purchase from the Company, the number of Shares set forth opposite such Investor's 
    name on Schedule A for the purchase price set forth therein.
    
    2. REPRESENTATIONS AND WARRANTIES OF THE COMPANY
    The Company represents and warrants to each Investor that:
    (a) The Company is duly incorporated and validly existing under Delaware law;
    (b) This Agreement has been duly authorized by the Company's Board of Directors;
    
    3. GOVERNING LAW
    This Agreement shall be governed by and construed in accordance with the laws of 
    the State of Delaware, without regard to conflict of law principles.
    
    4. DISPUTE RESOLUTION
    Any disputes arising under this Agreement shall be resolved exclusively in the 
    courts of the State of Delaware.
    """
    
    processor = USLegalProcessor()
    analysis = processor.analyze_document(text)
    print_analysis_results(analysis, "Securities Purchase Agreement Analysis")


def example_employment_agreement():
    """Example: Employment Agreement."""
    text = """
    EMPLOYMENT AGREEMENT
    
    This Employment Agreement (this "Agreement") is entered into between TechCorp Inc., 
    a California corporation (the "Company"), and John Smith (the "Employee").
    
    1. EMPLOYMENT
    The Company hereby employs the Employee, and the Employee accepts employment with 
    the Company, subject to the terms and conditions set forth herein.
    
    2. POSITION AND DUTIES
    The Employee shall serve as Chief Technology Officer and shall perform such duties 
    as are customarily associated with such position.
    
    3. COMPENSATION
    The Company shall pay the Employee an annual base salary of $200,000, payable in 
    accordance with the Company's standard payroll practices.
    
    4. BENEFITS
    The Employee shall be entitled to participate in all employee benefit plans 
    maintained by the Company, including health insurance, dental insurance, and 
    the Company's 401(k) plan.
    
    5. CONFIDENTIALITY
    The Employee acknowledges that during employment, the Employee will have access 
    to confidential information and trade secrets of the Company.
    
    6. NON-COMPETE
    During employment and for a period of twelve (12) months thereafter, the Employee 
    shall not engage in any business that competes with the Company within the 
    State of California.
    
    7. TERMINATION
    This Agreement may be terminated by either party at any time, with or without 
    cause, upon thirty (30) days' written notice. This is an at-will employment 
    relationship.
    
    8. GOVERNING LAW
    This Agreement shall be governed by the laws of the State of California and 
    shall comply with all applicable federal and state employment laws, including 
    the Fair Labor Standards Act (FLSA).
    """
    
    processor = USLegalProcessor()
    analysis = processor.analyze_document(text)
    print_analysis_results(analysis, "Employment Agreement Analysis")


def example_privacy_policy():
    """Example: Privacy Policy with CCPA compliance."""
    text = """
    PRIVACY POLICY
    
    Last Updated: [Date]
    
    This Privacy Policy describes how DataTech Inc. ("we," "us," or "our") collects, 
    uses, and shares personal information about California residents in connection 
    with our website and services.
    
    1. INFORMATION WE COLLECT
    We collect the following categories of personal information:
    - Identifiers (name, email address, IP address)
    - Commercial information (purchase history, browsing behavior)
    - Geolocation data
    - Biometric information (fingerprints for device access)
    - Internet activity (website interactions, search history)
    
    2. HOW WE USE PERSONAL INFORMATION
    We use personal information for the following business purposes:
    - Providing and improving our services
    - Marketing and advertising
    - Analytics and research
    - Security and fraud prevention
    
    3. SHARING OF PERSONAL INFORMATION
    We may share personal information with:
    - Service providers and vendors
    - Business partners for joint marketing
    - Third parties for advertising purposes
    
    4. CALIFORNIA CONSUMER PRIVACY ACT (CCPA) RIGHTS
    California residents have the following rights:
    - Right to know what personal information we collect
    - Right to delete personal information
    - Right to opt-out of the sale of personal information
    - Right to non-discrimination
    
    To exercise these rights, please contact us at privacy@datatech.com or 
    call 1-800-PRIVACY.
    
    5. DO NOT SELL MY PERSONAL INFORMATION
    California residents may opt-out of the sale of their personal information 
    by clicking the "Do Not Sell My Personal Information" link on our website.
    
    6. CHILDREN'S PRIVACY
    Our services are not directed to children under 13. We do not knowingly 
    collect personal information from children under 13. If we learn that we 
    have collected personal information from a child under 13, we will delete 
    such information in accordance with COPPA requirements.
    
    7. CONTACT INFORMATION
    For questions about this Privacy Policy, please contact:
    DataTech Inc.
    Privacy Officer
    123 Tech Street
    San Francisco, CA 94105
    privacy@datatech.com
    """
    
    processor = USLegalProcessor()
    analysis = processor.analyze_document(text)
    print_analysis_results(analysis, "Privacy Policy Analysis")


def example_ucc_sales_contract():
    """Example: UCC Sales Contract."""
    text = """
    SALES CONTRACT FOR GOODS
    
    This Sales Contract (this "Contract") is entered into between Manufacturing Corp, 
    a Delaware corporation ("Seller"), and Retail Inc., a New York corporation ("Buyer").
    
    1. SALE OF GOODS
    Seller agrees to sell and Buyer agrees to purchase the goods described in 
    Exhibit A (the "Goods"), which consist of industrial machinery and equipment 
    with a total value of $750,000.
    
    2. DELIVERY TERMS
    Delivery shall be FOB shipping point. Risk of loss shall pass to Buyer upon 
    delivery to the common carrier. Seller shall deliver the Goods within 60 days 
    of the execution of this Contract.
    
    3. WARRANTIES
    Seller warrants that:
    (a) The Goods are merchantable and fit for their intended purpose;
    (b) The Goods conform to the specifications set forth in Exhibit A;
    (c) Seller has good title to the Goods and the right to sell them;
    (d) The Goods are free from liens and encumbrances.
    
    SELLER DISCLAIMS ALL OTHER WARRANTIES, EXPRESS OR IMPLIED, INCLUDING 
    THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
    
    4. PAYMENT TERMS
    Buyer shall pay the purchase price of $750,000 as follows:
    - $150,000 upon execution of this Contract
    - $600,000 upon delivery and acceptance of the Goods
    
    5. INSPECTION AND ACCEPTANCE
    Buyer shall have 10 days after delivery to inspect the Goods and notify 
    Seller of any non-conformity. Failure to provide such notice shall constitute 
    acceptance of the Goods.
    
    6. REMEDIES
    In the event of breach, the non-breaching party shall be entitled to all 
    remedies available under the Uniform Commercial Code, including but not 
    limited to damages, specific performance, and cover.
    
    7. GOVERNING LAW
    This Contract shall be governed by the Uniform Commercial Code as adopted 
    in the State of Delaware and the laws of Delaware.
    """
    
    processor = USLegalProcessor()
    analysis = processor.analyze_document(text)
    print_analysis_results(analysis, "UCC Sales Contract Analysis")


def main():
    """Run all examples."""
    print("🇺🇸 US Legal System Processor Examples")
    print("=" * 60)
    
    try:
        # Run examples
        example_securities_agreement()
        example_employment_agreement()
        example_privacy_policy()
        example_ucc_sales_contract()
        
        print_separator("Summary")
        print("\n✅ All examples completed successfully!")
        print("\nThe US Legal Processor can analyze:")
        print("  • Federal law references (Securities Act, Exchange Act, etc.)")
        print("  • State jurisdiction and choice of law")
        print("  • UCC applicability and compliance")
        print("  • Securities law exemptions and requirements")
        print("  • Privacy law compliance (CCPA, GDPR, etc.)")
        print("  • Monetary amounts and contract terms")
        print("  • Document compliance and risk assessment")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()