"""Document text splitter for AI processing with legal document awareness."""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import tiktoken


@dataclass
class DocumentChunk:
    """Represents a chunk of document text with metadata."""
    content: str
    start_index: int
    end_index: int
    chunk_index: int
    token_count: int
    section_type: Optional[str] = None
    section_title: Optional[str] = None
    page_number: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentTextSplitter:
    """Intelligent text splitter for legal documents with context preservation."""
    
    def __init__(
        self,
        chunk_size: int = 4000,
        chunk_overlap: int = 200,
        model_name: str = "gpt-4",
        preserve_sections: bool = True
    ):
        """
        Initialize the text splitter.
        
        Args:
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Number of overlapping tokens between chunks
            model_name: OpenAI model name for token counting
            preserve_sections: Whether to try to keep sections intact
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.preserve_sections = preserve_sections
        
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback to cl100k_base encoding if model not found
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Legal document section patterns
        self.section_patterns = [
            r'^(\d+\.?\s+[A-Z][^.]*?)(?=\n|\r)',  # Numbered sections
            r'^([A-Z][A-Z\s]+)(?=\n|\r)',  # ALL CAPS headers
            r'^(WHEREAS[,\s].*?)(?=\n|\r)',  # WHEREAS clauses
            r'^(NOW THEREFORE[,\s].*?)(?=\n|\r)',  # NOW THEREFORE
            r'^(Article\s+\d+[:\.].*?)(?=\n|\r)',  # Article headers
            r'^(Section\s+\d+[:\.].*?)(?=\n|\r)',  # Section headers
            r'^(Clause\s+\d+[:\.].*?)(?=\n|\r)',  # Clause headers
            r'^([A-Z][a-z]+\s+[A-Z][a-z]+[:\.].*?)(?=\n|\r)',  # Title Case headers
        ]
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using the tokenizer."""
        return len(self.tokenizer.encode(text))
    
    def identify_sections(self, text: str) -> List[Dict[str, Any]]:
        """Identify document sections and their boundaries."""
        sections = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            for pattern in self.section_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    sections.append({
                        'title': match.group(1).strip(),
                        'line_number': i,
                        'start_index': text.find(line),
                        'type': self._classify_section_type(match.group(1))
                    })
                    break
        
        return sections
    
    def _classify_section_type(self, title: str) -> str:
        """Classify the type of section based on its title."""
        title_lower = title.lower()
        
        if 'whereas' in title_lower:
            return 'recital'
        elif 'now therefore' in title_lower or 'witnesseth' in title_lower:
            return 'operative'
        elif any(word in title_lower for word in ['definition', 'interpret']):
            return 'definitions'
        elif any(word in title_lower for word in ['term', 'duration', 'period']):
            return 'term'
        elif any(word in title_lower for word in ['payment', 'consideration', 'fee']):
            return 'payment'
        elif any(word in title_lower for word in ['obligation', 'covenant', 'undertaking']):
            return 'obligations'
        elif any(word in title_lower for word in ['termination', 'expiry', 'breach']):
            return 'termination'
        elif any(word in title_lower for word in ['dispute', 'arbitration', 'jurisdiction']):
            return 'dispute_resolution'
        elif any(word in title_lower for word in ['governing', 'applicable', 'law']):
            return 'governing_law'
        elif 'signature' in title_lower or 'execution' in title_lower:
            return 'execution'
        else:
            return 'general'
    
    def split_by_sections(self, text: str) -> List[DocumentChunk]:
        """Split text by identified sections while respecting token limits."""
        sections = self.identify_sections(text)
        chunks = []
        
        if not sections:
            # No sections found, use standard chunking
            return self.split_by_tokens(text)
        
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for i, section in enumerate(sections):
            # Get section content
            start_idx = section['start_index']
            end_idx = sections[i + 1]['start_index'] if i + 1 < len(sections) else len(text)
            section_content = text[start_idx:end_idx].strip()
            
            # Check if adding this section would exceed token limit
            potential_chunk = current_chunk + "\n\n" + section_content if current_chunk else section_content
            
            if self.count_tokens(potential_chunk) > self.chunk_size and current_chunk:
                # Create chunk from current content
                chunks.append(DocumentChunk(
                    content=current_chunk.strip(),
                    start_index=current_start,
                    end_index=start_idx,
                    chunk_index=chunk_index,
                    token_count=self.count_tokens(current_chunk),
                    section_type=sections[i-1]['type'] if i > 0 else 'general',
                    section_title=sections[i-1]['title'] if i > 0 else None
                ))
                
                chunk_index += 1
                current_chunk = section_content
                current_start = start_idx
            else:
                current_chunk = potential_chunk
                if not current_chunk.strip():
                    current_start = start_idx
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=len(text),
                chunk_index=chunk_index,
                token_count=self.count_tokens(current_chunk),
                section_type=sections[-1]['type'] if sections else 'general',
                section_title=sections[-1]['title'] if sections else None
            ))
        
        return chunks
    
    def split_by_tokens(self, text: str) -> List[DocumentChunk]:
        """Split text by token count with overlap."""
        chunks = []
        tokens = self.tokenizer.encode(text)
        
        start_idx = 0
        chunk_index = 0
        
        while start_idx < len(tokens):
            # Calculate end index for this chunk
            end_idx = min(start_idx + self.chunk_size, len(tokens))
            
            # Extract chunk tokens and decode
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            # Find character indices in original text
            char_start = len(self.tokenizer.decode(tokens[:start_idx]))
            char_end = len(self.tokenizer.decode(tokens[:end_idx]))
            
            chunks.append(DocumentChunk(
                content=chunk_text,
                start_index=char_start,
                end_index=char_end,
                chunk_index=chunk_index,
                token_count=len(chunk_tokens)
            ))
            
            chunk_index += 1
            
            # Move start index with overlap
            if end_idx == len(tokens):
                break
            start_idx = end_idx - self.chunk_overlap
        
        return chunks
    
    def split_document(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """
        Split document text into chunks using the best strategy.
        
        Args:
            text: Document text to split
            metadata: Optional metadata to include in chunks
            
        Returns:
            List of DocumentChunk objects
        """
        if not text.strip():
            return []
        
        # Choose splitting strategy
        if self.preserve_sections and len(text) > 1000:
            chunks = self.split_by_sections(text)
        else:
            chunks = self.split_by_tokens(text)
        
        # Add metadata to chunks
        if metadata:
            for chunk in chunks:
                chunk.metadata = metadata.copy()
        
        return chunks
    
    def get_chunk_with_context(
        self, 
        chunks: List[DocumentChunk], 
        target_chunk_index: int,
        context_chunks: int = 1
    ) -> str:
        """
        Get a chunk with surrounding context chunks.
        
        Args:
            chunks: List of document chunks
            target_chunk_index: Index of the target chunk
            context_chunks: Number of context chunks before and after
            
        Returns:
            Combined text with context
        """
        if not chunks or target_chunk_index >= len(chunks):
            return ""
        
        start_idx = max(0, target_chunk_index - context_chunks)
        end_idx = min(len(chunks), target_chunk_index + context_chunks + 1)
        
        context_text = []
        for i in range(start_idx, end_idx):
            chunk = chunks[i]
            if i == target_chunk_index:
                context_text.append(f"[TARGET CHUNK]\n{chunk.content}\n[/TARGET CHUNK]")
            else:
                context_text.append(chunk.content)
        
        return "\n\n".join(context_text)
    
    def merge_chunks(self, chunks: List[DocumentChunk]) -> str:
        """Merge chunks back into a single text."""
        return "\n\n".join(chunk.content for chunk in chunks)
    
    def get_statistics(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Get statistics about the chunks."""
        if not chunks:
            return {}
        
        total_tokens = sum(chunk.token_count for chunk in chunks)
        section_types = {}
        
        for chunk in chunks:
            if chunk.section_type:
                section_types[chunk.section_type] = section_types.get(chunk.section_type, 0) + 1
        
        return {
            'total_chunks': len(chunks),
            'total_tokens': total_tokens,
            'average_tokens_per_chunk': total_tokens / len(chunks),
            'min_tokens': min(chunk.token_count for chunk in chunks),
            'max_tokens': max(chunk.token_count for chunk in chunks),
            'section_types': section_types
        }