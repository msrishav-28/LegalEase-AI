"""
Example usage of the Comparative Jurisdiction Analyzer.

This example demonstrates how to use the ComparativeJurisdictionAnalyzer
for cross-border legal document analysis between Indian and US jurisdictions.
"""

import sys
import os
from decimal import Decimal

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.jurisdiction.comparative_analyzer import ComparativeJurisdictionAnalyzer
from app.core.jurisdiction.indian_processor import IndianState
from app.core.jurisdiction.us_processor import USState


def main():
    """Demonstrate comparative jurisdiction analysis."""
    
    # Sample cross-border software development agreement
    sample_agreement = """
    SOFTWARE DEVELOPMENT AND LICENSING AGREEMENT
    
    This Agreement is entered into on January 15, 2024, between:
    
    1. TechCorp Inc., a Delaware corporation with its principal place of business 
       at 123 Silicon Valley Drive, San Francisco, California 94105, USA ("Company")
    
    2. InfoSys Technologies Private Limited, a company incorporated under the 
       Companies Act, 2013, with its registered office at 456 IT Park, 
       Bangalore, Karnataka 560001, India ("Developer")
    
    RECITALS:
    WHEREAS, Company desires to engage Developer for software development services;
    WHEREAS, Developer has the expertise and resources to provide such services;
    
    NOW THEREFORE, the parties agree as follows:
    
    1. SERVICES: Developer shall provide custom software development services 
       including design, coding, testing, and documentation for a mobile 
       application as specified in Exhibit A.
    
    2. CONSIDERATION: Company shall pay Developer a total fee of $750,000 USD 
       (Seven Hundred Fifty Thousand US Dollars) payable in installments as 
       per the payment schedule in Exhibit B. This amount is inclusive of 
       applicable GST in India.
    
    3. INTELLECTUAL PROPERTY: All intellectual property rights in the developed 
       software shall vest exclusively with Company. Developer hereby assigns 
       all rights, title, and interest in the work product to Company.
    
    4. CONFIDENTIALITY: Both parties acknowledge that they may have access to 
       confidential information and agree to maintain strict confidentiality.
    
    5. GOVERNING LAW: This Agreement shall be governed by and construed in 
       accordance with the laws of the State of New York, without regard to 
       its conflict of laws principles.
    
    6. DISPUTE RESOLUTION: Any disputes arising out of or relating to this 
       Agreement shall be resolved through binding arbitration under the 
       rules of the International Chamber of Commerce (ICC) in Singapore.
    
    7. COMPLIANCE: Each party shall comply with all applicable laws and 
       regulations in their respective jurisdictions, including but not 
       limited to foreign exchange regulations, tax laws, and export controls.
    
    8. TERMINATION: Either party may terminate this Agreement upon 30 days 
       written notice. Upon termination, all work product shall be delivered 
       to Company and all confidential information shall be returned.
    
    9. STAMP DUTY: This Agreement is subject to stamp duty requirements 
       under Indian law and shall be appropriately stamped.
    
    10. REGISTRATION: The parties acknowledge that this Agreement may require 
        registration under applicable Indian laws.
    
    IN WITNESS WHEREOF, the parties have executed this Agreement on the date 
    first written above.
    
    TechCorp Inc.                    InfoSys Technologies Pvt. Ltd.
    
    By: _________________           By: _________________
    Name: John Smith                Name: Rajesh Kumar
    Title: CEO                      Title: Managing Director
    """
    
    print("=== Comparative Jurisdiction Analysis Example ===\n")
    
    # Initialize the comparative analyzer
    print("1. Initializing Comparative Jurisdiction Analyzer...")
    analyzer = ComparativeJurisdictionAnalyzer()
    print("   ✓ Analyzer initialized with Indian and US processors")
    print("   ✓ DTAA provisions loaded")
    print("   ✓ Governing law preferences configured")
    print("   ✓ Dispute resolution mechanisms initialized\n")
    
    # Perform cross-border analysis
    print("2. Performing Cross-Border Analysis...")
    print("   - Document: Software Development Agreement")
    print("   - Indian State: Karnataka")
    print("   - US State: New York")
    print("   - Processing...\n")
    
    try:
        result = analyzer.analyze_cross_border_document(
            sample_agreement,
            IndianState.KARNATAKA,
            USState.NEW_YORK
        )
        
        print("   ✓ Analysis completed successfully!\n")
        
        # Display results
        print("=== ANALYSIS RESULTS ===\n")
        
        # 1. Enforceability Comparison
        print("1. ENFORCEABILITY COMPARISON")
        print("-" * 40)
        enforceability = result.enforceability_comparison
        print(f"   India Enforceability Score: {enforceability.enforceability_score['india']:.2f}")
        print(f"   US Enforceability Score: {enforceability.enforceability_score['us']:.2f}")
        print(f"   Risk Level: {enforceability.risk_level.value.upper()}")
        print(f"   Cross-Border Risks: {len(enforceability.cross_border_risks)} identified")
        for risk in enforceability.cross_border_risks[:3]:  # Show first 3 risks
            print(f"     • {risk}")
        if len(enforceability.cross_border_risks) > 3:
            print(f"     ... and {len(enforceability.cross_border_risks) - 3} more")
        print()
        
        # 2. Formalities Comparison
        print("2. FORMALITIES COMPARISON")
        print("-" * 40)
        formalities = result.formalities_comparison
        
        # Stamp duty comparison
        stamp_duty = formalities.stamp_duty_comparison
        print("   Stamp Duty Requirements:")
        print(f"     India: Required ({stamp_duty['india']['rate']}% rate)")
        print(f"     US: {stamp_duty['us']['compliance_status'].replace('_', ' ').title()}")
        
        # Registration comparison
        registration = formalities.registration_comparison
        print("   Registration Requirements:")
        print(f"     India: {'Required' if registration['india']['required'] else 'Not Required'}")
        print(f"     US: {'Required' if registration['us']['required'] else 'Not Required'}")
        print()
        
        # 3. Tax Implications
        print("3. TAX IMPLICATIONS")
        print("-" * 40)
        tax = result.tax_implications
        print("   DTAA Benefits Available:")
        for benefit in tax.dtaa_benefits[:3]:  # Show first 3 benefits
            print(f"     • {benefit}")
        if len(tax.dtaa_benefits) > 3:
            print(f"     ... and {len(tax.dtaa_benefits) - 3} more")
        
        print("   Tax Recommendations:")
        for rec in tax.recommendations[:2]:  # Show first 2 recommendations
            print(f"     • {rec}")
        print()
        
        # 4. Compliance Gaps
        print("4. COMPLIANCE GAPS")
        print("-" * 40)
        print(f"   Total Gaps Identified: {len(result.compliance_gaps)}")
        for gap in result.compliance_gaps:
            print(f"   • {gap.description} (Priority: {gap.priority.upper()})")
            print(f"     Mitigation: {gap.mitigation_strategy}")
        print()
        
        # 5. Recommendations
        print("5. RECOMMENDATIONS")
        print("-" * 40)
        print(f"   Recommended Governing Law: {result.recommended_governing_law}")
        print(f"   Recommended Dispute Resolution: {result.recommended_dispute_resolution}")
        print()
        
        print("   Key Recommendations:")
        for i, rec in enumerate(result.recommendations[:3], 1):  # Show first 3 recommendations
            print(f"   {i}. {rec.category}: {rec.description}")
            print(f"      Priority: {rec.priority.upper()}")
            print(f"      Timeline: {rec.timeline}")
            print(f"      Cost: {rec.estimated_cost}")
            print()
        
        # 6. Overall Risk Assessment
        print("6. OVERALL RISK ASSESSMENT")
        print("-" * 40)
        print(f"   Risk Level: {result.overall_risk_assessment.upper()}")
        print()
        
        # 7. Implementation Roadmap
        print("7. IMPLEMENTATION ROADMAP")
        print("-" * 40)
        for step in result.implementation_roadmap[:6]:  # Show first 6 steps
            print(f"   {step}")
        if len(result.implementation_roadmap) > 6:
            print(f"   ... and {len(result.implementation_roadmap) - 6} more steps")
        print()
        
        # Summary
        print("=== SUMMARY ===")
        print(f"✓ Cross-border analysis completed for India-US transaction")
        print(f"✓ {len(result.compliance_gaps)} compliance gaps identified and addressed")
        print(f"✓ {len(result.recommendations)} actionable recommendations provided")
        print(f"✓ Implementation roadmap with {len(result.implementation_roadmap)} steps created")
        print(f"✓ Overall risk level: {result.overall_risk_assessment.upper()}")
        
    except Exception as e:
        print(f"   ✗ Analysis failed: {str(e)}")
        return
    
    print("\n=== Example completed successfully! ===")


def demonstrate_specific_features():
    """Demonstrate specific features of the comparative analyzer."""
    
    print("\n=== SPECIFIC FEATURES DEMONSTRATION ===\n")
    
    analyzer = ComparativeJurisdictionAnalyzer()
    
    # 1. DTAA Provisions
    print("1. INDIA-US DTAA PROVISIONS")
    print("-" * 40)
    dtaa = analyzer.dtaa_provisions
    
    print("   Withholding Tax Rates:")
    wht = dtaa['withholding_tax']
    print(f"     Dividends: {wht['dividends']['rate']}")
    print(f"     Interest: {wht['interest']['rate']}")
    print(f"     Royalties: {wht['royalties']['rate']}")
    print(f"     Technical Services: {wht['fees_for_technical_services']['rate']}")
    print()
    
    # 2. Governing Law Analysis
    print("2. GOVERNING LAW OPTIONS")
    print("-" * 40)
    gov_law = analyzer.governing_law_analysis
    
    for law_type, details in gov_law.items():
        print(f"   {law_type.replace('_', ' ').title()}:")
        print(f"     Advantages: {len(details['advantages'])} factors")
        print(f"     Suitable for: {', '.join(details['suitable_for'][:2])}")
    print()
    
    # 3. Dispute Resolution Mechanisms
    print("3. DISPUTE RESOLUTION OPTIONS")
    print("-" * 40)
    dispute_res = analyzer.dispute_resolution_mechanisms
    
    print("   Arbitration Institutions:")
    institutional = dispute_res['arbitration']['institutional']
    print(f"     Options: {', '.join(institutional['options'])}")
    print(f"     Enforcement: {institutional['enforcement']}")
    
    print("   Litigation:")
    for court_type, details in dispute_res['litigation'].items():
        print(f"     {court_type.replace('_', ' ').title()}: {details['enforcement']}")
    print()
    
    # 4. Transfer Pricing Rules
    print("4. TRANSFER PRICING COMPLIANCE")
    print("-" * 40)
    tp_rules = analyzer.transfer_pricing_rules
    
    for country, rules in tp_rules.items():
        print(f"   {country.upper()}:")
        print(f"     Threshold: {rules['threshold']}")
        print(f"     Documentation: {rules['documentation']}")
        print(f"     Penalties: {rules['penalties']}")
    print()


if __name__ == "__main__":
    main()
    demonstrate_specific_features()