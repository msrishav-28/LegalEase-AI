"""
Example usage of the Indian Legal Processor.

Demonstrates comprehensive analysis of Indian legal documents including
acts database integration, stamp duty calculation, GST analysis,
monetary amount extraction, and compliance checking.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.jurisdiction.indian_processor import IndianLegalProcessor, IndianState
from decimal import Decimal


def print_analysis_results(analysis, title):
    """Print formatted analysis results."""
    print(f"\n{'='*60}")
    print(f"ANALYSIS: {title}")
    print(f"{'='*60}")
    
    # Act References
    print(f"\n📚 INDIAN ACTS REFERENCED ({len(analysis.act_references)}):")
    for act in analysis.act_references:
        print(f"  • {act.act_name} (Year: {act.year}, Confidence: {act.confidence:.2f})")
        if act.sections:
            print(f"    Sections: {', '.join(act.sections)}")
    
    # Monetary Amounts
    print(f"\n💰 MONETARY AMOUNTS ({len(analysis.monetary_amounts)}):")
    for amount in analysis.monetary_amounts:
        print(f"  • {amount.formatted_amount} ({amount.original_text})")
    
    # Stamp Duty Analysis
    print(f"\n📋 STAMP DUTY ANALYSIS:")
    stamp_duty = analysis.stamp_duty
    print(f"  • State: {stamp_duty.state.value}")
    print(f"  • Document Type: {stamp_duty.document_type.value}")
    print(f"  • Consideration: {stamp_duty.consideration_amount}")
    print(f"  • Stamp Duty Rate: {stamp_duty.stamp_duty_rate}%")
    print(f"  • Calculated Duty: ₹{stamp_duty.calculated_duty}")
    print(f"  • Compliance Status: {stamp_duty.compliance_status}")
    
    # GST Analysis
    print(f"\n🏛️ GST ANALYSIS:")
    gst = analysis.gst_analysis
    print(f"  • Applicable: {gst.applicable}")
    if gst.gst_rate:
        print(f"  • GST Rate: {gst.gst_rate}%")
    if gst.hsn_codes:
        print(f"  • HSN Codes: {', '.join(gst.hsn_codes)}")
    print(f"  • Place of Supply: {gst.place_of_supply}")
    print(f"  • Registration Required: {gst.registration_required}")
    
    # Compliance Check
    print(f"\n✅ COMPLIANCE CHECK:")
    compliance = analysis.compliance_check
    print(f"  • Compliant: {compliance.compliant}")
    print(f"  • Risk Level: {compliance.risk_level}")
    if compliance.missing_clauses:
        print(f"  • Missing Clauses: {', '.join(compliance.missing_clauses)}")
    if compliance.violations:
        print(f"  • Violations: {', '.join(compliance.violations)}")
    
    # Registration Requirements
    if analysis.registration_requirements:
        print(f"\n📝 REGISTRATION REQUIREMENTS:")
        for req in analysis.registration_requirements:
            print(f"  • Required: {req.required}")
            print(f"  • Authority: {req.authority}")
            print(f"  • Time Limit: {req.time_limit}")
            print(f"  • Fees: ₹{req.fees}")
    
    # Applicable Laws
    print(f"\n⚖️ APPLICABLE LAWS ({len(analysis.applicable_laws)}):")
    for law in analysis.applicable_laws:
        print(f"  • {law}")
    
    # Jurisdiction Notes
    print(f"\n📍 JURISDICTION NOTES:")
    for note in analysis.jurisdiction_specific_notes:
        print(f"  • {note}")


def main():
    """Run examples of Indian legal document analysis."""
    
    # Initialize the processor
    processor = IndianLegalProcessor()
    
    # Example 1: Service Agreement
    service_agreement = """
    SERVICE AGREEMENT
    
    This Service Agreement is made under the Indian Contract Act, 1872 between 
    ABC Technologies Pvt. Ltd. and XYZ Consulting Services.
    
    The total consideration for services is Rs. 15,00,000 (Rupees Fifteen Lakhs only).
    
    GST at 18% shall be applicable on all services provided.
    
    This agreement is governed by the laws of Karnataka.
    
    Any disputes shall be resolved through arbitration as per the 
    Arbitration and Conciliation Act, 2015.
    """
    
    result1 = processor.analyze_document(service_agreement, IndianState.KARNATAKA)
    print_analysis_results(result1, "Service Agreement")
    
    # Example 2: Lease Agreement
    lease_agreement = """
    LEASE DEED
    
    This lease agreement is executed in Mumbai, Maharashtra for a period of 36 months.
    
    The monthly rent is Rs. 50,000 and security deposit is Rs. 3,00,000.
    
    The lease is governed by Transfer of Property Act, 1882.
    
    Registration is mandatory as per Registration Act, 1908 since the lease 
    period exceeds 11 months.
    
    Stamp duty shall be paid as per Maharashtra Stamp Act.
    """
    
    result2 = processor.analyze_document(lease_agreement, IndianState.MAHARASHTRA)
    print_analysis_results(result2, "Lease Agreement")
    
    # Example 3: Share Purchase Agreement
    share_purchase = """
    SHARE PURCHASE AGREEMENT
    
    This agreement is made under the Companies Act, 2013 and Indian Contract Act, 1872.
    
    The purchase price for 1000 equity shares is Rs. 25,00,000 (Rupees Twenty-Five Lakhs only).
    
    The transaction involves advisory services subject to GST at 18%.
    
    The shares are of ABC Private Limited, incorporated under Companies Act, 2013.
    
    Arbitration clause: Any disputes shall be resolved as per Arbitration and 
    Conciliation Act, 2015.
    
    Executed in New Delhi.
    """
    
    result3 = processor.analyze_document(share_purchase, IndianState.DELHI)
    print_analysis_results(result3, "Share Purchase Agreement")
    
    # Example 4: Complex Contract with Multiple Elements
    complex_contract = """
    COMPREHENSIVE BUSINESS AGREEMENT
    
    This agreement incorporates provisions from:
    - Indian Contract Act, 1872 for general contract terms
    - Companies Act, 2013 for corporate compliance
    - Goods and Services Tax Act, 2017 for tax obligations
    - Income Tax Act, 1961 for TDS provisions
    
    Financial Terms:
    - Base consideration: Rs. 1,50,00,000 (One Crore Fifty Lakhs)
    - Professional fees: Rs. 25,00,000 (Twenty-Five Lakhs)
    - GST applicable at 18% on services
    - TDS at 10% on professional fees
    
    The agreement is executed in Bangalore, Karnataka and shall be 
    governed by Karnataka laws.
    
    Registration requirements as per Registration Act, 1908 shall be complied with.
    
    Stamp duty calculation as per Karnataka Stamp Act.
    """
    
    result4 = processor.analyze_document(complex_contract, IndianState.KARNATAKA)
    print_analysis_results(result4, "Complex Business Agreement")
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()