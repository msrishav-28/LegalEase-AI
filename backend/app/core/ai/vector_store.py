"""Vector store implementation for semantic search and document embeddings."""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import hashlib

import pinecone
from openai import AsyncOpenAI
import tiktoken
from dataclasses import dataclass

from .text_splitter import DocumentTextSplitter, DocumentChunk
from ..exceptions import AIProcessingError, InvalidInputError


logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result from vector store."""
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    chunk_index: int
    section_type: Optional[str] = None


@dataclass
class DocumentEmbedding:
    """Represents a document embedding with metadata."""
    document_id: str
    chunk_id: str
    embedding: List[float]
    content: str
    metadata: Dict[str, Any]
    created_at: datetime


class VectorStoreManager:
    """
    Manages vector embeddings and semantic search using Pinecone.
    Handles document chunking, embedding generation, and similarity search.
    """
    
    def __init__(
        self,
        pinecone_api_key: str,
        pinecone_environment: str,
        index_name: str,
        openai_api_key: str,
        embedding_model: str = "text-embedding-ada-002",
        dimension: int = 1536
    ):
        """
        Initialize vector store manager.
        
        Args:
            pinecone_api_key: Pinecone API key
            pinecone_environment: Pinecone environment
            index_name: Pinecone index name
            openai_api_key: OpenAI API key for embeddings
            embedding_model: OpenAI embedding model
            dimension: Embedding dimension
        """
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_environment = pinecone_environment
        self.index_name = index_name
        self.embedding_model = embedding_model
        self.dimension = dimension
        
        # Initialize OpenAI client for embeddings
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        
        # Initialize text splitter
        self.text_splitter = DocumentTextSplitter(
            chunk_size=1000,  # Smaller chunks for better embeddings
            chunk_overlap=100
        )
        
        # Initialize Pinecone
        self._initialize_pinecone()
        
        # Token counter for cost estimation
        try:
            self.tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def _initialize_pinecone(self):
        """Initialize Pinecone connection and index."""
        try:
            pinecone.init(
                api_key=self.pinecone_api_key,
                environment=self.pinecone_environment
            )
            
            # Check if index exists, create if not
            if self.index_name not in pinecone.list_indexes():
                logger.info(f"Creating Pinecone index: {self.index_name}")
                pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    metadata_config={
                        "indexed": [
                            "document_id",
                            "document_type", 
                            "jurisdiction",
                            "section_type",
                            "created_date"
                        ]
                    }
                )
            
            self.index = pinecone.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise AIProcessingError(f"Vector store initialization failed: {str(e)}")
    
    async def add_document(
        self,
        document_id: str,
        document_content: str,
        document_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add a document to the vector store with embeddings.
        
        Args:
            document_id: Unique document identifier
            document_content: Document text content
            document_metadata: Document metadata (type, jurisdiction, etc.)
            
        Returns:
            Processing results with chunk count and embedding info
        """
        try:
            logger.info(f"Adding document {document_id} to vector store")
            
            # Split document into chunks
            chunks = self.text_splitter.split_document(
                document_content, 
                metadata=document_metadata
            )
            
            if not chunks:
                raise InvalidInputError("Document could not be split into chunks")
            
            # Generate embeddings for chunks
            embeddings_data = []
            batch_size = 10  # Process in batches to avoid rate limits
            
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i:i + batch_size]
                batch_embeddings = await self._generate_embeddings_batch(batch_chunks)
                
                for chunk, embedding in zip(batch_chunks, batch_embeddings):
                    chunk_id = self._generate_chunk_id(document_id, chunk.chunk_index)
                    
                    # Prepare metadata for Pinecone
                    pinecone_metadata = {
                        "document_id": document_id,
                        "chunk_index": chunk.chunk_index,
                        "content": chunk.content[:1000],  # Truncate for metadata
                        "section_type": chunk.section_type or "general",
                        "section_title": chunk.section_title or "",
                        "token_count": chunk.token_count,
                        "created_at": datetime.utcnow().isoformat(),
                        **document_metadata
                    }
                    
                    embeddings_data.append({
                        "id": chunk_id,
                        "values": embedding,
                        "metadata": pinecone_metadata
                    })
            
            # Upsert to Pinecone in batches
            batch_size = 100  # Pinecone batch size limit
            for i in range(0, len(embeddings_data), batch_size):
                batch = embeddings_data[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Successfully added {len(chunks)} chunks for document {document_id}")
            
            return {
                "document_id": document_id,
                "chunks_processed": len(chunks),
                "embeddings_created": len(embeddings_data),
                "total_tokens": sum(chunk.token_count for chunk in chunks),
                "processing_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to add document {document_id}: {str(e)}")
            raise AIProcessingError(f"Failed to add document to vector store: {str(e)}")
    
    async def search_similar_content(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[SearchResult]:
        """
        Search for similar content using semantic similarity.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Metadata filters for search
            include_metadata: Whether to include full metadata
            
        Returns:
            List of search results ordered by similarity
        """
        try:
            logger.info(f"Searching for similar content: '{query[:50]}...'")
            
            # Generate embedding for query
            query_embedding = await self._generate_embedding(query)
            
            # Prepare Pinecone query
            query_params = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": include_metadata
            }
            
            # Add filters if provided
            if filters:
                query_params["filter"] = self._build_pinecone_filter(filters)
            
            # Execute search
            search_response = self.index.query(**query_params)
            
            # Process results
            results = []
            for match in search_response.matches:
                metadata = match.metadata if include_metadata else {}
                
                result = SearchResult(
                    chunk_id=match.id,
                    document_id=metadata.get("document_id", ""),
                    content=metadata.get("content", ""),
                    score=match.score,
                    metadata=metadata,
                    chunk_index=metadata.get("chunk_index", 0),
                    section_type=metadata.get("section_type")
                )
                results.append(result)
            
            logger.info(f"Found {len(results)} similar content matches")
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            raise AIProcessingError(f"Failed to search similar content: {str(e)}")
    
    async def find_similar_clauses(
        self,
        clause_text: str,
        document_type: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        top_k: int = 5
    ) -> List[SearchResult]:
        """
        Find similar clauses across documents.
        
        Args:
            clause_text: The clause text to find similarities for
            document_type: Filter by document type
            jurisdiction: Filter by jurisdiction
            top_k: Number of similar clauses to return
            
        Returns:
            List of similar clauses with relevance scores
        """
        try:
            # Build filters
            filters = {}
            if document_type:
                filters["document_type"] = document_type
            if jurisdiction:
                filters["jurisdiction"] = jurisdiction
            
            # Search for similar content
            results = await self.search_similar_content(
                query=clause_text,
                top_k=top_k,
                filters=filters
            )
            
            # Filter results to focus on clause-like content
            clause_results = []
            for result in results:
                # Simple heuristic: clauses often contain legal keywords
                content_lower = result.content.lower()
                if any(keyword in content_lower for keyword in [
                    "shall", "will", "must", "agree", "covenant", "undertake",
                    "obligation", "right", "liability", "breach", "terminate"
                ]):
                    clause_results.append(result)
            
            return clause_results[:top_k]
            
        except Exception as e:
            logger.error(f"Similar clause search failed: {str(e)}")
            raise AIProcessingError(f"Failed to find similar clauses: {str(e)}")
    
    async def search_by_document_section(
        self,
        section_type: str,
        query: Optional[str] = None,
        document_type: Optional[str] = None,
        top_k: int = 10
    ) -> List[SearchResult]:
        """
        Search within specific document sections.
        
        Args:
            section_type: Type of section (definitions, obligations, etc.)
            query: Optional query text for semantic search
            document_type: Filter by document type
            top_k: Number of results to return
            
        Returns:
            List of search results from specified sections
        """
        try:
            # Build filters
            filters = {"section_type": section_type}
            if document_type:
                filters["document_type"] = document_type
            
            if query:
                # Semantic search within section type
                results = await self.search_similar_content(
                    query=query,
                    top_k=top_k,
                    filters=filters
                )
            else:
                # Get all content from section type (using dummy query)
                results = await self.search_similar_content(
                    query=section_type,  # Use section type as query
                    top_k=top_k,
                    filters=filters
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Section search failed: {str(e)}")
            raise AIProcessingError(f"Failed to search document sections: {str(e)}")
    
    async def get_document_chunks(
        self,
        document_id: str,
        include_embeddings: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document.
        
        Args:
            document_id: Document identifier
            include_embeddings: Whether to include embedding vectors
            
        Returns:
            List of document chunks with metadata
        """
        try:
            # Query Pinecone for all chunks of the document
            query_response = self.index.query(
                vector=[0.0] * self.dimension,  # Dummy vector
                top_k=1000,  # Large number to get all chunks
                filter={"document_id": document_id},
                include_metadata=True,
                include_values=include_embeddings
            )
            
            chunks = []
            for match in query_response.matches:
                chunk_data = {
                    "chunk_id": match.id,
                    "metadata": match.metadata,
                    "score": match.score
                }
                
                if include_embeddings:
                    chunk_data["embedding"] = match.values
                
                chunks.append(chunk_data)
            
            # Sort by chunk index
            chunks.sort(key=lambda x: x["metadata"].get("chunk_index", 0))
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to get document chunks: {str(e)}")
            raise AIProcessingError(f"Failed to retrieve document chunks: {str(e)}")
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete all chunks for a document from vector store.
        
        Args:
            document_id: Document identifier
            
        Returns:
            True if deletion was successful
        """
        try:
            logger.info(f"Deleting document {document_id} from vector store")
            
            # Get all chunk IDs for the document
            chunks = await self.get_document_chunks(document_id)
            chunk_ids = [chunk["chunk_id"] for chunk in chunks]
            
            if chunk_ids:
                # Delete chunks in batches
                batch_size = 100
                for i in range(0, len(chunk_ids), batch_size):
                    batch = chunk_ids[i:i + batch_size]
                    self.index.delete(ids=batch)
                
                logger.info(f"Deleted {len(chunk_ids)} chunks for document {document_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            return False
    
    async def update_document_metadata(
        self,
        document_id: str,
        metadata_updates: Dict[str, Any]
    ) -> bool:
        """
        Update metadata for all chunks of a document.
        
        Args:
            document_id: Document identifier
            metadata_updates: Metadata fields to update
            
        Returns:
            True if update was successful
        """
        try:
            # Get all chunks for the document
            chunks = await self.get_document_chunks(document_id, include_embeddings=True)
            
            # Update metadata for each chunk
            updates = []
            for chunk in chunks:
                updated_metadata = chunk["metadata"].copy()
                updated_metadata.update(metadata_updates)
                updated_metadata["updated_at"] = datetime.utcnow().isoformat()
                
                updates.append({
                    "id": chunk["chunk_id"],
                    "values": chunk.get("embedding", []),
                    "metadata": updated_metadata
                })
            
            # Upsert updated chunks
            if updates:
                batch_size = 100
                for i in range(0, len(updates), batch_size):
                    batch = updates[i:i + batch_size]
                    self.index.upsert(vectors=batch)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document metadata: {str(e)}")
            return False
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index."""
        try:
            stats = self.index.describe_index_stats()
            
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": dict(stats.namespaces) if stats.namespaces else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            return {}
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise AIProcessingError(f"Embedding generation failed: {str(e)}")
    
    async def _generate_embeddings_batch(self, chunks: List[DocumentChunk]) -> List[List[float]]:
        """Generate embeddings for a batch of chunks."""
        try:
            # Prepare texts for embedding
            texts = [chunk.content for chunk in chunks]
            
            # Generate embeddings
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            return [data.embedding for data in response.data]
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {str(e)}")
            raise AIProcessingError(f"Batch embedding generation failed: {str(e)}")
    
    def _generate_chunk_id(self, document_id: str, chunk_index: int) -> str:
        """Generate unique chunk ID."""
        return f"{document_id}_chunk_{chunk_index}"
    
    def _build_pinecone_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build Pinecone filter from simple filter dict."""
        pinecone_filter = {}
        
        for key, value in filters.items():
            if isinstance(value, list):
                pinecone_filter[key] = {"$in": value}
            else:
                pinecone_filter[key] = {"$eq": value}
        
        return pinecone_filter
    
    def estimate_embedding_cost(self, text: str) -> Dict[str, Any]:
        """Estimate cost for embedding generation."""
        token_count = len(self.tokenizer.encode(text))
        
        # OpenAI pricing for text-embedding-ada-002 (as of 2024)
        cost_per_1k_tokens = 0.0001  # $0.0001 per 1K tokens
        estimated_cost = (token_count / 1000) * cost_per_1k_tokens
        
        return {
            "token_count": token_count,
            "estimated_cost_usd": estimated_cost,
            "model": self.embedding_model
        }