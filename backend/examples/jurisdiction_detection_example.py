"""
Example demonstrating the jurisdiction detection engine.

This example shows how to use the JurisdictionDetector to identify
Indian and US legal documents with confidence scoring.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.jurisdiction.detector import JurisdictionDetector, Jurisdiction


def main():
    """Demonstrate jurisdiction detection with various document types."""
    
    # Initialize the detector
    detector = JurisdictionDetector()
    
    # Example documents
    documents = {
        "Indian Contract": """
        This Agreement is made under the Indian Contract Act, 1872, between 
        ABC Private Limited, a company incorporated in Mumbai, Maharashtra, 
        and XYZ LLP, registered in Gujarat. The consideration is Rs. 50 lakhs. 
        Any disputes shall be resolved by the High Court of Bombay. 
        Stamp duty as per Maharashtra Stamp Act applies.
        """,
        
        "US Corporate Agreement": """
        This Agreement shall be governed by Delaware law and the Uniform Commercial Code.
        ABC Corporation, a Delaware corporation, and XYZ LLC, a California limited 
        liability company, agree to the terms. The consideration is $500,000. 
        Disputes shall be resolved in Federal District Court for the District of Delaware. 
        The parties comply with SEC regulations.
        """,
        
        "Cross-Border Transaction": """
        This Agreement is governed by both Indian Contract Act, 1872 and Delaware law.
        Disputes shall be resolved through arbitration under ICC rules. The parties 
        acknowledge SEC regulations and SEBI compliance requirements. Payment shall 
        be made in both USD and INR as per RBI and Federal Reserve guidelines.
        """,
        
        "Ambiguous Document": """
        This is a simple agreement between two parties. The consideration is 
        one hundred thousand units of currency. Both parties agree to the terms
        and conditions set forth herein.
        """
    }
    
    print("=== Jurisdiction Detection Examples ===\n")
    
    for doc_name, text in documents.items():
        print(f"Document: {doc_name}")
        print("-" * 50)
        
        # Detect jurisdiction
        result = detector.detect_jurisdiction(text)
        
        # Get summary
        summary = detector.get_jurisdiction_summary(result)
        
        # Display results
        print(f"Jurisdiction: {result.jurisdiction.value}")
        print(f"Confidence: {summary['confidence_percentage']}% ({summary['confidence_level']})")
        
        if result.us_state:
            print(f"US State: {result.us_state}")
        if result.indian_state:
            print(f"Indian State: {result.indian_state}")
            
        print(f"Total Indicators: {len(result.detected_elements)}")
        print("Key Indicators:")
        for element in result.detected_elements[:5]:  # Show top 5
            print(f"  - {element}")
            
        if len(result.detected_elements) > 5:
            print(f"  ... and {len(result.detected_elements) - 5} more")
            
        print(f"Scores: India={result.scores['india']:.1f}, USA={result.scores['usa']:.1f}")
        
        if 'note' in summary:
            print(f"Note: {summary['note']}")
            
        print("\n")


if __name__ == "__main__":
    main()