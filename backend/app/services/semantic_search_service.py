"""Semantic search service for document analysis and clause finding."""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from app.core.ai.vector_store import VectorStoreManager, SearchResult
from app.core.ai.llm_orchestrator import LLMOrchestrator
from app.core.ai.prompt_templates import JurisdictionType
from app.core.exceptions import AIProcessingError, InvalidInputError
from app.config import get_settings


logger = logging.getLogger(__name__)


class SemanticSearchService:
    """
    Service for semantic search and document similarity analysis.
    Combines vector search with AI-powered analysis for enhanced results.
    """
    
    def __init__(self):
        """Initialize semantic search service."""
        settings = get_settings()
        
        # Initialize vector store manager
        self.vector_store = VectorStoreManager(
            pinecone_api_key=settings.pinecone_api_key,
            pinecone_environment=settings.pinecone_environment,
            index_name=settings.pinecone_index_name,
            openai_api_key=settings.openai_api_key
        )
        
        # Initialize LLM orchestrator for enhanced analysis
        self.llm_orchestrator = LLMOrchestrator(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=settings.ai_temperature
        )
    
    async def add_document_to_search_index(
        self,
        document_id: str,
        document_content: str,
        document_type: str,
        jurisdiction: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a document to the search index with embeddings.
        
        Args:
            document_id: Unique document identifier
            document_content: Document text content
            document_type: Type of document (contract, agreement, etc.)
            jurisdiction: Legal jurisdiction
            additional_metadata: Additional metadata to store
            
        Returns:
            Processing results
        """
        try:
            logger.info(f"Adding document {document_id} to search index")
            
            # Prepare document metadata
            metadata = {
                "document_type": document_type,
                "jurisdiction": jurisdiction or "unknown",
                "created_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "indexed_at": datetime.utcnow().isoformat()
            }
            
            if additional_metadata:
                metadata.update(additional_metadata)
            
            # Add to vector store
            result = await self.vector_store.add_document(
                document_id=document_id,
                document_content=document_content,
                document_metadata=metadata
            )
            
            logger.info(f"Successfully indexed document {document_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to add document to search index: {str(e)}")
            raise AIProcessingError(f"Failed to index document: {str(e)}")
    
    async def search_documents(
        self,
        query: str,
        document_type: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        top_k: int = 10,
        min_score: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search documents using semantic similarity.
        
        Args:
            query: Search query text
            document_type: Filter by document type
            jurisdiction: Filter by jurisdiction
            top_k: Maximum number of results
            min_score: Minimum similarity score threshold
            
        Returns:
            List of search results with enhanced metadata
        """
        try:
            logger.info(f"Searching documents for query: '{query[:50]}...'")
            
            # Build filters
            filters = {}
            if document_type:
                filters["document_type"] = document_type
            if jurisdiction:
                filters["jurisdiction"] = jurisdiction
            
            # Perform vector search
            search_results = await self.vector_store.search_similar_content(
                query=query,
                top_k=top_k,
                filters=filters
            )
            
            # Filter by minimum score and enhance results
            enhanced_results = []
            for result in search_results:
                if result.score >= min_score:
                    enhanced_result = await self._enhance_search_result(result, query)
                    enhanced_results.append(enhanced_result)
            
            logger.info(f"Found {len(enhanced_results)} relevant documents")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Document search failed: {str(e)}")
            raise AIProcessingError(f"Failed to search documents: {str(e)}")
    
    async def find_similar_clauses(
        self,
        clause_text: str,
        document_type: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        top_k: int = 5,
        include_analysis: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find clauses similar to the provided clause text.
        
        Args:
            clause_text: The clause text to find similarities for
            document_type: Filter by document type
            jurisdiction: Filter by jurisdiction
            top_k: Number of similar clauses to return
            include_analysis: Whether to include AI analysis of similarities
            
        Returns:
            List of similar clauses with analysis
        """
        try:
            logger.info(f"Finding similar clauses for: '{clause_text[:50]}...'")
            
            # Search for similar clauses
            similar_clauses = await self.vector_store.find_similar_clauses(
                clause_text=clause_text,
                document_type=document_type,
                jurisdiction=jurisdiction,
                top_k=top_k
            )
            
            # Enhance results with AI analysis
            enhanced_clauses = []
            for clause_result in similar_clauses:
                enhanced_clause = {
                    "clause_id": clause_result.chunk_id,
                    "document_id": clause_result.document_id,
                    "content": clause_result.content,
                    "similarity_score": clause_result.score,
                    "metadata": clause_result.metadata,
                    "section_type": clause_result.section_type
                }
                
                if include_analysis:
                    # Add AI analysis of the similarity
                    analysis = await self._analyze_clause_similarity(
                        original_clause=clause_text,
                        similar_clause=clause_result.content,
                        jurisdiction=clause_result.metadata.get("jurisdiction")
                    )
                    enhanced_clause["similarity_analysis"] = analysis
                
                enhanced_clauses.append(enhanced_clause)
            
            logger.info(f"Found {len(enhanced_clauses)} similar clauses")
            return enhanced_clauses
            
        except Exception as e:
            logger.error(f"Similar clause search failed: {str(e)}")
            raise AIProcessingError(f"Failed to find similar clauses: {str(e)}")
    
    async def search_by_legal_concept(
        self,
        legal_concept: str,
        jurisdiction: Optional[str] = None,
        document_type: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for documents containing specific legal concepts.
        
        Args:
            legal_concept: Legal concept to search for (e.g., "force majeure", "indemnification")
            jurisdiction: Filter by jurisdiction
            document_type: Filter by document type
            top_k: Number of results to return
            
        Returns:
            List of documents containing the legal concept
        """
        try:
            logger.info(f"Searching for legal concept: '{legal_concept}'")
            
            # Expand the legal concept with related terms
            expanded_query = await self._expand_legal_concept_query(legal_concept, jurisdiction)
            
            # Search using expanded query
            results = await self.search_documents(
                query=expanded_query,
                document_type=document_type,
                jurisdiction=jurisdiction,
                top_k=top_k,
                min_score=0.6  # Lower threshold for concept search
            )
            
            # Add concept-specific analysis
            enhanced_results = []
            for result in results:
                concept_analysis = await self._analyze_legal_concept_usage(
                    content=result["content"],
                    legal_concept=legal_concept,
                    jurisdiction=jurisdiction
                )
                
                result["concept_analysis"] = concept_analysis
                enhanced_results.append(result)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Legal concept search failed: {str(e)}")
            raise AIProcessingError(f"Failed to search legal concept: {str(e)}")
    
    async def find_document_precedents(
        self,
        document_content: str,
        document_type: str,
        jurisdiction: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find precedent documents similar to the provided document.
        
        Args:
            document_content: Content of the document to find precedents for
            document_type: Type of document
            jurisdiction: Legal jurisdiction
            top_k: Number of precedents to return
            
        Returns:
            List of precedent documents with similarity analysis
        """
        try:
            logger.info(f"Finding precedents for {document_type} document")
            
            # Extract key clauses from the document for search
            key_clauses = await self._extract_key_clauses(document_content, document_type)
            
            precedents = []
            
            # Search for similar documents using key clauses
            for clause in key_clauses[:3]:  # Use top 3 key clauses
                similar_docs = await self.search_documents(
                    query=clause,
                    document_type=document_type,
                    jurisdiction=jurisdiction,
                    top_k=top_k
                )
                
                for doc in similar_docs:
                    # Avoid duplicates
                    if not any(p["document_id"] == doc["document_id"] for p in precedents):
                        precedents.append(doc)
            
            # Sort by similarity score and limit results
            precedents.sort(key=lambda x: x["similarity_score"], reverse=True)
            precedents = precedents[:top_k]
            
            # Add precedent analysis
            for precedent in precedents:
                precedent_analysis = await self._analyze_document_precedent(
                    original_content=document_content,
                    precedent_content=precedent["content"],
                    jurisdiction=jurisdiction
                )
                precedent["precedent_analysis"] = precedent_analysis
            
            logger.info(f"Found {len(precedents)} precedent documents")
            return precedents
            
        except Exception as e:
            logger.error(f"Precedent search failed: {str(e)}")
            raise AIProcessingError(f"Failed to find precedents: {str(e)}")
    
    async def search_by_document_section(
        self,
        section_type: str,
        query: Optional[str] = None,
        document_type: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search within specific document sections.
        
        Args:
            section_type: Type of section (definitions, obligations, termination, etc.)
            query: Optional query text for semantic search within sections
            document_type: Filter by document type
            jurisdiction: Filter by jurisdiction
            top_k: Number of results to return
            
        Returns:
            List of section content with metadata
        """
        try:
            logger.info(f"Searching in {section_type} sections")
            
            # Search by section type
            results = await self.vector_store.search_by_document_section(
                section_type=section_type,
                query=query,
                document_type=document_type,
                top_k=top_k
            )
            
            # Enhance results with section analysis
            enhanced_results = []
            for result in results:
                enhanced_result = {
                    "chunk_id": result.chunk_id,
                    "document_id": result.document_id,
                    "content": result.content,
                    "similarity_score": result.score,
                    "section_type": result.section_type,
                    "metadata": result.metadata
                }
                
                # Add section-specific analysis if query provided
                if query:
                    section_analysis = await self._analyze_section_relevance(
                        section_content=result.content,
                        query=query,
                        section_type=section_type
                    )
                    enhanced_result["section_analysis"] = section_analysis
                
                enhanced_results.append(enhanced_result)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Section search failed: {str(e)}")
            raise AIProcessingError(f"Failed to search sections: {str(e)}")
    
    async def remove_document_from_index(self, document_id: str) -> bool:
        """
        Remove a document from the search index.
        
        Args:
            document_id: Document identifier to remove
            
        Returns:
            True if removal was successful
        """
        try:
            logger.info(f"Removing document {document_id} from search index")
            
            success = await self.vector_store.delete_document(document_id)
            
            if success:
                logger.info(f"Successfully removed document {document_id}")
            else:
                logger.warning(f"Failed to remove document {document_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to remove document from index: {str(e)}")
            return False
    
    async def get_search_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the search index."""
        try:
            stats = await self.vector_store.get_index_stats()
            
            return {
                "index_stats": stats,
                "service_info": {
                    "embedding_model": self.vector_store.embedding_model,
                    "dimension": self.vector_store.dimension,
                    "index_name": self.vector_store.index_name
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _enhance_search_result(self, result: SearchResult, query: str) -> Dict[str, Any]:
        """Enhance search result with additional analysis."""
        return {
            "document_id": result.document_id,
            "chunk_id": result.chunk_id,
            "content": result.content,
            "similarity_score": result.score,
            "metadata": result.metadata,
            "section_type": result.section_type,
            "relevance_summary": await self._generate_relevance_summary(result.content, query)
        }
    
    async def _generate_relevance_summary(self, content: str, query: str) -> str:
        """Generate a summary of why the content is relevant to the query."""
        try:
            # Use LLM to generate relevance summary
            jurisdiction = JurisdictionType.UNKNOWN
            
            summary = await self.llm_orchestrator.analyze_jurisdiction_specific(
                document_content=f"Content: {content}\n\nQuery: {query}",
                jurisdiction=jurisdiction,
                analysis_type="relevance_summary"
            )
            
            return summary.get("result", "Relevant content found")
            
        except Exception:
            return "Content matches search criteria"
    
    async def _analyze_clause_similarity(
        self,
        original_clause: str,
        similar_clause: str,
        jurisdiction: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze similarity between two clauses."""
        try:
            jurisdiction_type = JurisdictionType(jurisdiction) if jurisdiction else JurisdictionType.UNKNOWN
            
            analysis = await self.llm_orchestrator.analyze_jurisdiction_specific(
                document_content=f"Original: {original_clause}\n\nSimilar: {similar_clause}",
                jurisdiction=jurisdiction_type,
                analysis_type="clause_similarity_analysis"
            )
            
            return analysis
            
        except Exception as e:
            return {"error": str(e), "analysis": "Similarity analysis unavailable"}
    
    async def _expand_legal_concept_query(self, legal_concept: str, jurisdiction: Optional[str]) -> str:
        """Expand legal concept with related terms for better search."""
        try:
            jurisdiction_type = JurisdictionType(jurisdiction) if jurisdiction else JurisdictionType.UNKNOWN
            
            expansion = await self.llm_orchestrator.analyze_jurisdiction_specific(
                document_content=legal_concept,
                jurisdiction=jurisdiction_type,
                analysis_type="legal_concept_expansion"
            )
            
            return expansion.get("result", legal_concept)
            
        except Exception:
            return legal_concept
    
    async def _analyze_legal_concept_usage(
        self,
        content: str,
        legal_concept: str,
        jurisdiction: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze how a legal concept is used in the content."""
        try:
            jurisdiction_type = JurisdictionType(jurisdiction) if jurisdiction else JurisdictionType.UNKNOWN
            
            analysis = await self.llm_orchestrator.analyze_jurisdiction_specific(
                document_content=f"Content: {content}\n\nConcept: {legal_concept}",
                jurisdiction=jurisdiction_type,
                analysis_type="legal_concept_usage_analysis"
            )
            
            return analysis
            
        except Exception as e:
            return {"error": str(e), "analysis": "Concept analysis unavailable"}
    
    async def _extract_key_clauses(self, document_content: str, document_type: str) -> List[str]:
        """Extract key clauses from a document for precedent search."""
        try:
            analysis = await self.llm_orchestrator.analyze_document(
                document_content=document_content,
                document_type=document_type,
                jurisdiction=JurisdictionType.UNKNOWN,
                analysis_type="key_clause_extraction"
            )
            
            # Extract clauses from analysis result
            clauses = analysis.get("key_clauses", [])
            if isinstance(clauses, list):
                return clauses
            else:
                return [str(clauses)]
                
        except Exception:
            # Fallback: use first few sentences
            sentences = document_content.split('. ')
            return sentences[:5]
    
    async def _analyze_document_precedent(
        self,
        original_content: str,
        precedent_content: str,
        jurisdiction: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze how a document serves as precedent."""
        try:
            jurisdiction_type = JurisdictionType(jurisdiction) if jurisdiction else JurisdictionType.UNKNOWN
            
            analysis = await self.llm_orchestrator.analyze_jurisdiction_specific(
                document_content=f"Original: {original_content[:500]}...\n\nPrecedent: {precedent_content[:500]}...",
                jurisdiction=jurisdiction_type,
                analysis_type="precedent_analysis"
            )
            
            return analysis
            
        except Exception as e:
            return {"error": str(e), "analysis": "Precedent analysis unavailable"}
    
    async def _analyze_section_relevance(
        self,
        section_content: str,
        query: str,
        section_type: str
    ) -> Dict[str, Any]:
        """Analyze relevance of section content to query."""
        try:
            analysis = await self.llm_orchestrator.analyze_document(
                document_content=f"Section ({section_type}): {section_content}\n\nQuery: {query}",
                document_type="section",
                jurisdiction=JurisdictionType.UNKNOWN,
                analysis_type="section_relevance_analysis"
            )
            
            return analysis
            
        except Exception as e:
            return {"error": str(e), "analysis": "Section analysis unavailable"}