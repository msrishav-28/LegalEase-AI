"""
Document processing module for PDF text extraction and OCR.
"""
import io
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

import pdfplumber
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import fitz  # PyMuPDF for image extraction

logger = logging.getLogger(__name__)


class ExtractionMethod(Enum):
    """Enumeration of text extraction methods."""
    TEXT = "text"
    OCR = "ocr"
    HYBRID = "hybrid"


@dataclass
class ExtractionResult:
    """Result of PDF text extraction."""
    text: str
    method: ExtractionMethod
    page_count: int
    confidence: float
    metadata: Dict
    errors: List[str]


class PDFExtractor:
    """
    PDF text extraction class with OCR fallback capabilities.
    
    Supports both direct text extraction and OCR processing for scanned documents.
    Includes image preprocessing pipeline for improved OCR accuracy.
    """
    
    def __init__(
        self,
        ocr_confidence_threshold: float = 0.6,
        text_extraction_threshold: int = 50,
        tesseract_config: str = "--oem 3 --psm 6"
    ):
        """
        Initialize PDFExtractor with configuration parameters.
        
        Args:
            ocr_confidence_threshold: Minimum confidence for OCR results
            text_extraction_threshold: Minimum characters for text extraction success
            tesseract_config: Tesseract OCR configuration string
        """
        self.ocr_confidence_threshold = ocr_confidence_threshold
        self.text_extraction_threshold = text_extraction_threshold
        self.tesseract_config = tesseract_config
        
    def extract_text(self, pdf_path: Union[str, Path, bytes]) -> ExtractionResult:
        """
        Extract text from PDF using the most appropriate method.
        
        Args:
            pdf_path: Path to PDF file or PDF bytes
            
        Returns:
            ExtractionResult with extracted text and metadata
        """
        errors = []
        
        try:
            # First attempt: Direct text extraction
            text_result = self._extract_text_direct(pdf_path)
            
            if self._is_extraction_successful(text_result.text):
                logger.info(f"Successfully extracted text directly from PDF")
                return text_result
                
            logger.info("Direct text extraction insufficient, attempting OCR")
            
            # Second attempt: OCR extraction
            ocr_result = self._extract_text_ocr(pdf_path)
            
            if self._is_extraction_successful(ocr_result.text):
                return ocr_result
                
            # If both methods have some content, use hybrid approach
            if text_result.text.strip() or ocr_result.text.strip():
                return self._combine_extraction_results(text_result, ocr_result)
                
            # If all methods fail, return best available result
            return ExtractionResult(
                text="",
                method=ExtractionMethod.TEXT,
                page_count=0,
                confidence=0.0,
                metadata={},
                errors=["Failed to extract any text from PDF"]
            )
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            return ExtractionResult(
                text="",
                method=ExtractionMethod.TEXT,
                page_count=0,
                confidence=0.0,
                metadata={},
                errors=[f"Extraction error: {str(e)}"]
            )
    
    def _extract_text_direct(self, pdf_path: Union[str, Path, bytes]) -> ExtractionResult:
        """Extract text directly from PDF using pdfplumber."""
        text_content = []
        metadata = {}
        errors = []
        
        try:
            if isinstance(pdf_path, bytes):
                pdf_file = io.BytesIO(pdf_path)
            else:
                pdf_file = pdf_path
                
            with pdfplumber.open(pdf_file) as pdf:
                metadata = {
                    'page_count': len(pdf.pages),
                    'metadata': pdf.metadata or {}
                }
                
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                    except Exception as e:
                        errors.append(f"Error extracting text from page {page_num}: {str(e)}")
                        
            full_text = "\n\n".join(text_content)
            confidence = self._calculate_text_confidence(full_text)
            
            return ExtractionResult(
                text=full_text,
                method=ExtractionMethod.TEXT,
                page_count=metadata.get('page_count', 0),
                confidence=confidence,
                metadata=metadata,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"Direct text extraction failed: {str(e)}")
            return ExtractionResult(
                text="",
                method=ExtractionMethod.TEXT,
                page_count=0,
                confidence=0.0,
                metadata={},
                errors=[f"Direct extraction error: {str(e)}"]
            )
    
    def _extract_text_ocr(self, pdf_path: Union[str, Path, bytes]) -> ExtractionResult:
        """Extract text using OCR on PDF pages converted to images."""
        text_content = []
        metadata = {}
        errors = []
        confidences = []
        
        try:
            if isinstance(pdf_path, bytes):
                pdf_document = fitz.open(stream=pdf_path, filetype="pdf")
            else:
                pdf_document = fitz.open(pdf_path)
                
            metadata['page_count'] = pdf_document.page_count
            
            for page_num in range(pdf_document.page_count):
                try:
                    page = pdf_document[page_num]
                    
                    # Convert page to image
                    mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    
                    # Preprocess image for better OCR
                    image = Image.open(io.BytesIO(img_data))
                    processed_image = self._preprocess_image(image)
                    
                    # Perform OCR
                    ocr_data = pytesseract.image_to_data(
                        processed_image, 
                        config=self.tesseract_config,
                        output_type=pytesseract.Output.DICT
                    )
                    
                    # Extract text and confidence
                    page_text, page_confidence = self._extract_text_from_ocr_data(ocr_data)
                    
                    if page_text.strip():
                        text_content.append(page_text)
                        confidences.append(page_confidence)
                        
                except Exception as e:
                    errors.append(f"OCR error on page {page_num + 1}: {str(e)}")
                    
            pdf_document.close()
            
            full_text = "\n\n".join(text_content)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return ExtractionResult(
                text=full_text,
                method=ExtractionMethod.OCR,
                page_count=metadata.get('page_count', 0),
                confidence=avg_confidence,
                metadata=metadata,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return ExtractionResult(
                text="",
                method=ExtractionMethod.OCR,
                page_count=0,
                confidence=0.0,
                metadata={},
                errors=[f"OCR extraction error: {str(e)}"]
            )
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Apply slight blur to reduce noise
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
    
    def _extract_text_from_ocr_data(self, ocr_data: Dict) -> Tuple[str, float]:
        """
        Extract text and confidence from Tesseract OCR data.
        
        Args:
            ocr_data: Dictionary from pytesseract image_to_data
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        words = []
        confidences = []
        
        for i, conf in enumerate(ocr_data['conf']):
            if int(conf) > 0:  # Filter out low confidence detections
                text = ocr_data['text'][i].strip()
                if text:
                    words.append(text)
                    confidences.append(int(conf))
        
        text = ' '.join(words)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return text, avg_confidence / 100.0  # Convert to 0-1 scale
    
    def _calculate_text_confidence(self, text: str) -> float:
        """
        Calculate confidence score for directly extracted text.
        
        Args:
            text: Extracted text string
            
        Returns:
            Confidence score between 0 and 1
        """
        if not text.strip():
            return 0.0
            
        # Simple heuristics for text quality
        char_count = len(text)
        word_count = len(text.split())
        
        # Check for reasonable word-to-character ratio
        if word_count == 0:
            return 0.1
            
        avg_word_length = char_count / word_count
        
        # Reasonable average word length suggests good extraction
        if 3 <= avg_word_length <= 8:
            confidence = 0.9
        elif 2 <= avg_word_length <= 10:
            confidence = 0.7
        else:
            confidence = 0.5
            
        # Boost confidence for longer texts
        if char_count > 1000:
            confidence = min(1.0, confidence + 0.1)
            
        return confidence
    
    def _is_extraction_successful(self, text: str) -> bool:
        """
        Determine if text extraction was successful based on content length.
        
        Args:
            text: Extracted text
            
        Returns:
            True if extraction is considered successful
        """
        return len(text.strip()) >= self.text_extraction_threshold
    
    def _combine_extraction_results(
        self, 
        text_result: ExtractionResult, 
        ocr_result: ExtractionResult
    ) -> ExtractionResult:
        """
        Combine results from both text and OCR extraction methods.
        
        Args:
            text_result: Result from direct text extraction
            ocr_result: Result from OCR extraction
            
        Returns:
            Combined ExtractionResult
        """
        # Use the result with higher confidence
        if text_result.confidence >= ocr_result.confidence:
            primary_result = text_result
            secondary_text = ocr_result.text
        else:
            primary_result = ocr_result
            secondary_text = text_result.text
        
        # Combine texts if both have content
        combined_text = primary_result.text
        if secondary_text.strip() and len(secondary_text) > len(primary_result.text) * 0.1:
            combined_text += f"\n\n--- Alternative Extraction ---\n{secondary_text}"
        
        return ExtractionResult(
            text=combined_text,
            method=ExtractionMethod.HYBRID,
            page_count=max(text_result.page_count, ocr_result.page_count),
            confidence=max(text_result.confidence, ocr_result.confidence),
            metadata={**text_result.metadata, **ocr_result.metadata},
            errors=text_result.errors + ocr_result.errors
        )


class DocumentType(Enum):
    """Enumeration of document types."""
    CONTRACT = "contract"
    AGREEMENT = "agreement"
    LEASE = "lease"
    NDA = "nda"
    EMPLOYMENT = "employment"
    CORPORATE = "corporate"
    LITIGATION = "litigation"
    REGULATORY = "regulatory"
    UNKNOWN = "unknown"


@dataclass
class DocumentSection:
    """Represents a section within a document."""
    title: str
    content: str
    level: int  # Heading level (1-6)
    start_position: int
    end_position: int
    subsections: List['DocumentSection']


@dataclass
class DocumentStructure:
    """Result of document structure analysis."""
    document_type: DocumentType
    sections: List[DocumentSection]
    parties: List[str]
    dates: List[str]
    key_terms: List[str]
    metadata: Dict
    confidence: float


class DocumentStructureAnalyzer:
    """
    Analyzes document structure to identify sections, headers, and document type.
    
    Provides document section extraction with metadata and text cleaning/normalization.
    """
    
    def __init__(self):
        """Initialize DocumentStructureAnalyzer."""
        # Common legal document patterns
        self.section_patterns = [
            r'^(\d+\.?\s*[A-Z][^.\n]*?)\.?\s*$',  # Numbered sections
            r'^([A-Z][A-Z\s]{2,}):?\s*$',  # ALL CAPS headers
            r'^([A-Z][a-z\s]{3,}):?\s*$',  # Title case headers
            r'^([IVX]+\.?\s*[A-Z][^.\n]*?)\.?\s*$',  # Roman numeral sections
            r'^\(([a-z])\)\s*([A-Z][^.\n]*?)\.?\s*$',  # Lettered subsections
        ]
        
        # Document type indicators
        self.document_type_patterns = {
            DocumentType.CONTRACT: [
                r'\bcontract\b', r'\bagreement\b', r'\bparties\b', r'\bconsideration\b'
            ],
            DocumentType.LEASE: [
                r'\blease\b', r'\blessor\b', r'\blessee\b', r'\brent\b', r'\bpremises\b'
            ],
            DocumentType.NDA: [
                r'\bnon.?disclosure\b', r'\bconfidential(?:ity)?\b', r'\bproprietary\b', r'\bnda\b'
            ],
            DocumentType.EMPLOYMENT: [
                r'\bemployment\b', r'\bemployee\b', r'\bemployer\b', r'\bsalary\b'
            ],
            DocumentType.CORPORATE: [
                r'\bcorporation\b', r'\bboard\b', r'\bshareholder\b', r'\bdirector\b'
            ]
        }
        
        # Party identification patterns
        self.party_patterns = [
            r'\b([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\("?[A-Z][a-z]+"?\)',
            r'\b([A-Z][A-Z\s&]+(?:LLC|INC|CORP|LTD|CO)\.?)\b',
            r'between\s+([^,]+?)\s+and\s+([^,]+?)(?:\s|,)',
            r'party\s+of\s+the\s+first\s+part[,:]?\s*([^,\n]+)',
            r'party\s+of\s+the\s+second\s+part[,:]?\s*([^,\n]+)'
        ]
        
        # Date patterns
        self.date_patterns = [
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            r'\b([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})\b',
            r'\b(\d{1,2}(?:st|nd|rd|th)?\s+day\s+of\s+[A-Z][a-z]+,?\s+\d{4})\b'
        ]
    
    def analyze_structure(self, text: str) -> DocumentStructure:
        """
        Analyze document structure and extract sections, metadata.
        
        Args:
            text: Document text content
            
        Returns:
            DocumentStructure with analyzed components
        """
        # Clean and normalize text
        cleaned_text = self._clean_text(text)
        
        # Extract sections
        sections = self._extract_sections(cleaned_text)
        
        # Detect document type
        doc_type = self._detect_document_type(cleaned_text)
        
        # Extract parties
        parties = self._extract_parties(cleaned_text)
        
        # Extract dates
        dates = self._extract_dates(cleaned_text)
        
        # Extract key terms
        key_terms = self._extract_key_terms(cleaned_text)
        
        # Calculate confidence
        confidence = self._calculate_structure_confidence(sections, doc_type, parties)
        
        return DocumentStructure(
            document_type=doc_type,
            sections=sections,
            parties=parties,
            dates=dates,
            key_terms=key_terms,
            metadata={
                'total_sections': len(sections),
                'text_length': len(cleaned_text),
                'has_numbered_sections': any('.' in s.title for s in sections),
                'max_section_level': max([s.level for s in sections], default=0)
            },
            confidence=confidence
        )
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize document text.
        
        Args:
            text: Raw document text
            
        Returns:
            Cleaned and normalized text
        """
        import re
        
        # Normalize line breaks first
        text = re.sub(r'\r\n|\r', '\n', text)
        
        # Split into lines for processing
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip likely page numbers (standalone numbers)
            if re.match(r'^\s*\d+\s*$', line):
                continue
                
            # Skip very short lines that are likely artifacts
            if len(line) < 3:
                continue
                
            # Skip lines with only special characters
            if re.match(r'^[^\w\s]*$', line):
                continue
            
            # Remove excessive whitespace within the line
            line = re.sub(r'\s+', ' ', line)
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _extract_sections(self, text: str) -> List[DocumentSection]:
        """
        Extract document sections based on headers and structure.
        
        Args:
            text: Cleaned document text
            
        Returns:
            List of DocumentSection objects
        """
        import re
        
        sections = []
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if line matches section header patterns
            section_match = None
            level = 1
            
            for pattern in self.section_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    section_match = match
                    # Determine level based on pattern type
                    if pattern.startswith(r'^\('):  # Lettered subsections
                        level = 3
                    elif pattern.startswith(r'^([IVX]+'):  # Roman numerals
                        level = 2
                    elif re.match(r'^\d+\.\d+', line):  # Numbered subsections
                        level = 2
                    break
            
            if section_match:
                # Save previous section
                if current_section:
                    current_section.content = '\n'.join(current_content).strip()
                    current_section.end_position = i
                    sections.append(current_section)
                
                # Start new section
                title = section_match.group(1).strip()
                current_section = DocumentSection(
                    title=title,
                    content="",
                    level=level,
                    start_position=i,
                    end_position=i,
                    subsections=[]
                )
                current_content = []
            else:
                # Add to current section content
                if current_section:
                    current_content.append(line)
                else:
                    # Create a default section for content before first header
                    if not sections:
                        current_section = DocumentSection(
                            title="Preamble",
                            content="",
                            level=1,
                            start_position=0,
                            end_position=0,
                            subsections=[]
                        )
                        current_content = [line]
        
        # Save final section
        if current_section:
            current_section.content = '\n'.join(current_content).strip()
            current_section.end_position = len(lines)
            sections.append(current_section)
        
        # Organize subsections
        sections = self._organize_subsections(sections)
        
        return sections
    
    def _organize_subsections(self, sections: List[DocumentSection]) -> List[DocumentSection]:
        """
        Organize sections into hierarchical structure with subsections.
        
        Args:
            sections: Flat list of sections
            
        Returns:
            Hierarchically organized sections
        """
        if not sections:
            return []
        
        organized = []
        stack = []
        
        for section in sections:
            # Pop sections from stack that are at same or higher level
            while stack and stack[-1].level >= section.level:
                stack.pop()
            
            if stack:
                # Add as subsection to parent
                stack[-1].subsections.append(section)
            else:
                # Add as top-level section
                organized.append(section)
            
            stack.append(section)
        
        return organized
    
    def _detect_document_type(self, text: str) -> DocumentType:
        """
        Detect document type based on content patterns.
        
        Args:
            text: Document text
            
        Returns:
            Detected DocumentType
        """
        import re
        
        text_lower = text.lower()
        type_scores = {}
        
        for doc_type, patterns in self.document_type_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            type_scores[doc_type] = score
        
        # Special handling for NDA - only if it has strong NDA indicators AND significantly lower contract indicators
        nda_score = type_scores.get(DocumentType.NDA, 0)
        contract_score = type_scores.get(DocumentType.CONTRACT, 0)
        
        # Check for explicit NDA title
        if re.search(r'\bnon.?disclosure\s+agreement\b', text_lower) and nda_score >= 2:
            return DocumentType.NDA
        
        # Only classify as NDA if NDA score is significantly higher than contract score
        if nda_score >= 4 and contract_score < nda_score - 1:
            return DocumentType.NDA
        
        # Return type with highest score, or UNKNOWN if no clear match
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                return best_type
        
        return DocumentType.UNKNOWN
    
    def _extract_parties(self, text: str) -> List[str]:
        """
        Extract party names from document text.
        
        Args:
            text: Document text
            
        Returns:
            List of identified party names
        """
        import re
        
        parties = set()
        
        for pattern in self.party_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                for group in match.groups():
                    if group:
                        party = group.strip().strip('"\'()[]')
                        if len(party) > 2 and not party.isdigit():
                            parties.add(party)
        
        return list(parties)[:10]  # Limit to reasonable number
    
    def _extract_dates(self, text: str) -> List[str]:
        """
        Extract dates from document text.
        
        Args:
            text: Document text
            
        Returns:
            List of identified dates
        """
        import re
        
        dates = set()
        
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group(1).strip()
                dates.add(date_str)
        
        return list(dates)[:20]  # Limit to reasonable number
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key legal terms from document text.
        
        Args:
            text: Document text
            
        Returns:
            List of key terms
        """
        import re
        from collections import Counter
        
        # Common legal terms to identify
        legal_terms = [
            'consideration', 'covenant', 'warranty', 'indemnify', 'liability',
            'breach', 'termination', 'force majeure', 'arbitration', 'jurisdiction',
            'governing law', 'confidential', 'proprietary', 'intellectual property',
            'damages', 'remedy', 'cure period', 'notice', 'consent', 'assignment'
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for term in legal_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                found_terms.append(term)
        
        # Also extract capitalized terms that might be defined terms
        defined_terms = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
        term_counts = Counter(defined_terms)
        
        # Add frequently occurring capitalized terms
        for term, count in term_counts.most_common(10):
            if count > 1 and len(term) > 3:
                found_terms.append(term)
        
        return found_terms[:20]  # Limit to reasonable number
    
    def _calculate_structure_confidence(
        self, 
        sections: List[DocumentSection], 
        doc_type: DocumentType, 
        parties: List[str]
    ) -> float:
        """
        Calculate confidence score for structure analysis.
        
        Args:
            sections: Extracted sections
            doc_type: Detected document type
            parties: Extracted parties
            
        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.0
        
        # Base confidence from sections
        if sections:
            confidence += 0.2
            if len(sections) > 2:
                confidence += 0.2
            # Check if sections have meaningful structure
            numbered_sections = sum(1 for s in sections if any(c.isdigit() for c in s.title))
            if numbered_sections > 0:
                confidence += 0.1
        
        # Boost for detected document type
        if doc_type != DocumentType.UNKNOWN:
            confidence += 0.3
        
        # Boost for identified parties
        if parties:
            confidence += 0.2
        
        # Boost for hierarchical structure
        if any(s.subsections for s in sections):
            confidence += 0.1
        
        # Penalty for sections that look like random text
        if sections:
            avg_section_length = sum(len(s.content) for s in sections) / len(sections)
            if avg_section_length < 20:  # Very short sections suggest poor structure
                confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))