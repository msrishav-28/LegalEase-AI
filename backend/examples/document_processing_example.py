"""
Example demonstrating PDF text extraction and document structure analysis.
"""
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core import PDFExtractor, DocumentStructureAnalyzer


def process_document_example():
    """
    Example showing complete document processing workflow.
    """
    # Initialize processors
    pdf_extractor = PDFExtractor()
    structure_analyzer = DocumentStructureAnalyzer()
    
    # Example: Process a PDF file (this would be a real PDF path in practice)
    # For demonstration, we'll use sample text
    sample_legal_text = """
    SERVICE AGREEMENT
    
    This Service Agreement ("Agreement") is entered into on January 15, 2024,
    between TechCorp Inc. ("Company") and Legal Consulting LLC ("Consultant").
    
    1. SCOPE OF WORK
    
    The Consultant shall provide legal advisory services as described herein.
    All work shall be performed in accordance with professional standards.
    
    1.1 Deliverables
    Consultant shall deliver monthly reports and legal opinions as requested.
    
    2. COMPENSATION
    
    Company shall pay Consultant $10,000 per month for services rendered.
    Payment shall be made within 30 days of invoice receipt.
    
    3. CONFIDENTIALITY
    
    Both parties agree to maintain strict confidentiality of all proprietary
    information shared during the course of this engagement.
    
    4. TERM AND TERMINATION
    
    This agreement shall commence on February 1, 2024 and continue for
    one year unless terminated earlier by either party with 60 days notice.
    
    5. GOVERNING LAW
    
    This agreement shall be governed by the laws of Delaware.
    """
    
    print("=== Document Processing Example ===\n")
    
    # Step 1: Extract text (in real scenario, this would be from PDF)
    print("1. Text Extraction Results:")
    print(f"   - Text length: {len(sample_legal_text)} characters")
    print(f"   - Method: Direct text (simulated)")
    print(f"   - Confidence: 0.95")
    print()
    
    # Step 2: Analyze document structure
    print("2. Document Structure Analysis:")
    structure_result = structure_analyzer.analyze_structure(sample_legal_text)
    
    print(f"   - Document Type: {structure_result.document_type.value}")
    print(f"   - Confidence: {structure_result.confidence:.2f}")
    print(f"   - Total Sections: {len(structure_result.sections)}")
    print()
    
    # Step 3: Display extracted sections
    print("3. Extracted Sections:")
    for i, section in enumerate(structure_result.sections, 1):
        print(f"   {i}. {section.title} (Level {section.level})")
        if section.subsections:
            for j, subsection in enumerate(section.subsections, 1):
                print(f"      {i}.{j} {subsection.title}")
    print()
    
    # Step 4: Display extracted parties
    print("4. Identified Parties:")
    for party in structure_result.parties:
        print(f"   - {party}")
    print()
    
    # Step 5: Display extracted dates
    print("5. Identified Dates:")
    for date in structure_result.dates:
        print(f"   - {date}")
    print()
    
    # Step 6: Display key terms
    print("6. Key Legal Terms:")
    for term in structure_result.key_terms[:10]:  # Show first 10
        print(f"   - {term}")
    print()
    
    # Step 7: Display metadata
    print("7. Document Metadata:")
    for key, value in structure_result.metadata.items():
        print(f"   - {key}: {value}")
    
    print("\n=== Processing Complete ===")


if __name__ == "__main__":
    process_document_example()