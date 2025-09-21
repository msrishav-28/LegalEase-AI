"""LLM Orchestrator for managing AI interactions with jurisdiction-aware prompts."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from datetime import datetime
import openai
from openai import AsyncOpenAI
import tiktoken

from .prompt_templates import PromptTemplateManager, JurisdictionType
from .text_splitter import DocumentTextSplitter, DocumentChunk
from .conversation_memory import ConversationMemoryManager, MessageRole
from ..exceptions import AIProcessingError, RateLimitError, InvalidInputError


logger = logging.getLogger(__name__)


class LLMOrchestrator:
    """
    Orchestrates LLM interactions with jurisdiction-aware prompts and context management.
    Handles retry logic, rate limiting, and conversation memory.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        rate_limit_delay: float = 60.0,
        temperature: float = 0.1,
        max_tokens: int = 4000
    ):
        """
        Initialize the LLM orchestrator.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries (exponential backoff)
            rate_limit_delay: Delay when rate limited
            temperature: Model temperature for response generation
            max_tokens: Maximum tokens in response
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_delay = rate_limit_delay
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize components
        self.prompt_manager = PromptTemplateManager()
        self.text_splitter = DocumentTextSplitter(model_name=model)
        self.memory_manager = ConversationMemoryManager()
        
        # Token counting
        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    async def analyze_document(
        self,
        document_content: str,
        document_type: str,
        jurisdiction: JurisdictionType,
        analysis_type: str = "executive_summary",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a document with jurisdiction-specific prompts.
        
        Args:
            document_content: The document text to analyze
            document_type: Type of document (contract, agreement, etc.)
            jurisdiction: Legal jurisdiction for analysis
            analysis_type: Type of analysis to perform
            context: Additional context for analysis
            
        Returns:
            Analysis results as structured data
        """
        try:
            # Prepare context
            analysis_context = context or {}
            
            # Get appropriate prompts
            system_prompt = self.prompt_manager.get_system_prompt(jurisdiction)
            analysis_prompt = self.prompt_manager.get_analysis_prompt(
                analysis_type,
                document_content=document_content,
                jurisdiction=jurisdiction.value,
                document_type=document_type,
                context=json.dumps(analysis_context)
            )
            
            # Check if document needs chunking
            if self._count_tokens(document_content) > 12000:  # Leave room for prompts
                return await self._analyze_large_document(
                    document_content, document_type, jurisdiction, analysis_type, context
                )
            
            # Single request for smaller documents
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = await self._make_api_call(messages)
            
            # Parse and structure response
            result = self._parse_analysis_response(response, analysis_type)
            
            # Add metadata
            result["metadata"] = {
                "jurisdiction": jurisdiction.value,
                "document_type": document_type,
                "analysis_type": analysis_type,
                "timestamp": datetime.utcnow().isoformat(),
                "model": self.model,
                "token_usage": self._estimate_token_usage(messages, response)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Document analysis failed: {str(e)}")
            raise AIProcessingError(f"Failed to analyze document: {str(e)}")
    
    async def chat_with_document(
        self,
        session_id: str,
        question: str,
        document_content: Optional[str] = None,
        jurisdiction: Optional[JurisdictionType] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Interactive chat about a document with context awareness.
        
        Args:
            session_id: Conversation session ID
            question: User's question
            document_content: Document text (if not in session context)
            jurisdiction: Legal jurisdiction
            user_id: User identifier
            
        Returns:
            Chat response with metadata
        """
        try:
            # Get or create session
            session = self.memory_manager.get_session(session_id)
            if not session and user_id:
                session = self.memory_manager.create_session(
                    session_id=session_id,
                    user_id=user_id,
                    jurisdiction=jurisdiction.value if jurisdiction else None,
                    context_metadata={"document_content": document_content}
                )
            
            if not session:
                raise InvalidInputError("Invalid session or missing user_id")
            
            # Add user message to conversation
            self.memory_manager.add_message(
                session_id=session_id,
                role=MessageRole.USER,
                content=question,
                token_count=self._count_tokens(question)
            )
            
            # Prepare context
            conversation_history = self.memory_manager.get_conversation_history(
                session_id, max_messages=10
            )
            
            # Get document content from session if not provided
            if not document_content and session.context_metadata:
                document_content = session.context_metadata.get("document_content", "")
            
            # Determine jurisdiction
            if not jurisdiction and session.jurisdiction:
                jurisdiction = JurisdictionType(session.jurisdiction)
            elif not jurisdiction:
                jurisdiction = JurisdictionType.UNKNOWN
            
            # Build chat prompt
            system_prompt = self.prompt_manager.get_system_prompt(jurisdiction)
            chat_prompt = self.prompt_manager.get_chat_prompt(
                "contextual_qa",
                document_content=document_content or "No document provided",
                jurisdiction=jurisdiction.value,
                conversation_history=json.dumps(conversation_history[-5:]),  # Recent context
                question=question
            )
            
            # Prepare messages
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history[-8:])  # Recent conversation
            messages.append({"role": "user", "content": chat_prompt})
            
            # Get AI response
            response = await self._make_api_call(messages)
            
            # Add assistant response to conversation
            self.memory_manager.add_message(
                session_id=session_id,
                role=MessageRole.ASSISTANT,
                content=response,
                token_count=self._count_tokens(response)
            )
            
            # Parse response for structured data
            parsed_response = self._parse_chat_response(response)
            
            return {
                "response": response,
                "parsed_response": parsed_response,
                "session_id": session_id,
                "metadata": {
                    "jurisdiction": jurisdiction.value,
                    "timestamp": datetime.utcnow().isoformat(),
                    "model": self.model,
                    "conversation_length": len(session.messages),
                    "token_usage": self._estimate_token_usage(messages, response)
                }
            }
            
        except Exception as e:
            logger.error(f"Chat interaction failed: {str(e)}")
            raise AIProcessingError(f"Failed to process chat: {str(e)}")
    
    async def stream_chat_response(
        self,
        session_id: str,
        question: str,
        document_content: Optional[str] = None,
        jurisdiction: Optional[JurisdictionType] = None,
        user_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response for real-time user experience.
        
        Args:
            session_id: Conversation session ID
            question: User's question
            document_content: Document text
            jurisdiction: Legal jurisdiction
            user_id: User identifier
            
        Yields:
            Streaming response chunks
        """
        try:
            # Similar setup to chat_with_document but with streaming
            session = self.memory_manager.get_session(session_id)
            if not session and user_id:
                session = self.memory_manager.create_session(
                    session_id=session_id,
                    user_id=user_id,
                    jurisdiction=jurisdiction.value if jurisdiction else None,
                    context_metadata={"document_content": document_content}
                )
            
            if not session:
                raise InvalidInputError("Invalid session or missing user_id")
            
            # Add user message
            self.memory_manager.add_message(
                session_id=session_id,
                role=MessageRole.USER,
                content=question,
                token_count=self._count_tokens(question)
            )
            
            # Prepare messages (similar to chat_with_document)
            conversation_history = self.memory_manager.get_conversation_history(
                session_id, max_messages=10
            )
            
            if not document_content and session.context_metadata:
                document_content = session.context_metadata.get("document_content", "")
            
            if not jurisdiction and session.jurisdiction:
                jurisdiction = JurisdictionType(session.jurisdiction)
            elif not jurisdiction:
                jurisdiction = JurisdictionType.UNKNOWN
            
            system_prompt = self.prompt_manager.get_system_prompt(jurisdiction)
            chat_prompt = self.prompt_manager.get_chat_prompt(
                "contextual_qa",
                document_content=document_content or "No document provided",
                jurisdiction=jurisdiction.value,
                conversation_history=json.dumps(conversation_history[-5:]),
                question=question
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history[-8:])
            messages.append({"role": "user", "content": chat_prompt})
            
            # Stream response
            full_response = ""
            async for chunk in self._stream_api_call(messages):
                full_response += chunk
                yield chunk
            
            # Add complete response to conversation
            self.memory_manager.add_message(
                session_id=session_id,
                role=MessageRole.ASSISTANT,
                content=full_response,
                token_count=self._count_tokens(full_response)
            )
            
        except Exception as e:
            logger.error(f"Streaming chat failed: {str(e)}")
            yield f"Error: {str(e)}"
    
    async def analyze_jurisdiction_specific(
        self,
        document_content: str,
        jurisdiction: JurisdictionType,
        analysis_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform jurisdiction-specific analysis (stamp duty, UCC, etc.).
        
        Args:
            document_content: Document text
            jurisdiction: Legal jurisdiction
            analysis_type: Specific analysis type
            **kwargs: Additional parameters for analysis
            
        Returns:
            Jurisdiction-specific analysis results
        """
        try:
            system_prompt = self.prompt_manager.get_system_prompt(jurisdiction)
            analysis_prompt = self.prompt_manager.get_jurisdiction_prompt(
                analysis_type,
                document_content=document_content,
                **kwargs
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = await self._make_api_call(messages)
            
            return {
                "analysis_type": analysis_type,
                "jurisdiction": jurisdiction.value,
                "result": response,
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "model": self.model,
                    "parameters": kwargs
                }
            }
            
        except Exception as e:
            logger.error(f"Jurisdiction-specific analysis failed: {str(e)}")
            raise AIProcessingError(f"Failed to perform {analysis_type} analysis: {str(e)}")
    
    async def _analyze_large_document(
        self,
        document_content: str,
        document_type: str,
        jurisdiction: JurisdictionType,
        analysis_type: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze large documents by chunking and aggregating results."""
        chunks = self.text_splitter.split_document(document_content)
        
        if not chunks:
            raise InvalidInputError("Document could not be split into chunks")
        
        # Analyze each chunk
        chunk_results = []
        for chunk in chunks:
            chunk_analysis = await self.analyze_document(
                chunk.content,
                document_type,
                jurisdiction,
                analysis_type,
                context
            )
            chunk_results.append({
                "chunk_index": chunk.chunk_index,
                "section_type": chunk.section_type,
                "analysis": chunk_analysis
            })
        
        # Aggregate results
        aggregated_result = await self._aggregate_chunk_results(
            chunk_results, analysis_type, jurisdiction
        )
        
        return aggregated_result
    
    async def _aggregate_chunk_results(
        self,
        chunk_results: List[Dict[str, Any]],
        analysis_type: str,
        jurisdiction: JurisdictionType
    ) -> Dict[str, Any]:
        """Aggregate analysis results from multiple chunks."""
        # Create aggregation prompt
        system_prompt = self.prompt_manager.get_system_prompt(jurisdiction)
        
        aggregation_prompt = f"""
        Aggregate the following chunk analysis results into a comprehensive {analysis_type}:
        
        Chunk Results:
        {json.dumps(chunk_results, indent=2)}
        
        Provide a unified analysis that:
        1. Synthesizes findings across all chunks
        2. Identifies patterns and themes
        3. Resolves any contradictions
        4. Provides comprehensive conclusions
        5. Maintains jurisdiction-specific context
        
        Format as structured JSON matching the original analysis format.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": aggregation_prompt}
        ]
        
        response = await self._make_api_call(messages)
        
        return {
            "aggregated_analysis": self._parse_analysis_response(response, analysis_type),
            "chunk_count": len(chunk_results),
            "individual_chunks": chunk_results,
            "metadata": {
                "jurisdiction": jurisdiction.value,
                "analysis_type": analysis_type,
                "aggregation_timestamp": datetime.utcnow().isoformat(),
                "model": self.model
            }
        }
    
    async def _make_api_call(self, messages: List[Dict[str, str]]) -> str:
        """Make API call with retry logic and error handling."""
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                return response.choices[0].message.content
                
            except openai.RateLimitError as e:
                logger.warning(f"Rate limit hit, attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.rate_limit_delay)
                else:
                    raise RateLimitError("Rate limit exceeded after all retries")
                    
            except openai.APIError as e:
                logger.error(f"OpenAI API error, attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise AIProcessingError(f"API error after all retries: {str(e)}")
                    
            except Exception as e:
                logger.error(f"Unexpected error, attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise AIProcessingError(f"Unexpected error after all retries: {str(e)}")
    
    async def _stream_api_call(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Make streaming API call with error handling."""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Streaming API call failed: {str(e)}")
            yield f"Error: {str(e)}"
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenizer.encode(text))
    
    def _estimate_token_usage(self, messages: List[Dict[str, str]], response: str) -> Dict[str, int]:
        """Estimate token usage for the API call."""
        prompt_tokens = sum(self._count_tokens(msg["content"]) for msg in messages)
        completion_tokens = self._count_tokens(response)
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }
    
    def _parse_analysis_response(self, response: str, analysis_type: str) -> Dict[str, Any]:
        """Parse and structure analysis response."""
        try:
            # Try to parse as JSON first
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback to structured text parsing
            return {
                "raw_response": response,
                "analysis_type": analysis_type,
                "parsed": False,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _parse_chat_response(self, response: str) -> Dict[str, Any]:
        """Parse chat response for structured elements."""
        # Extract confidence level, citations, etc.
        confidence_match = None
        citations = []
        
        # Simple parsing - can be enhanced with more sophisticated NLP
        if "confidence:" in response.lower():
            # Extract confidence level
            pass
        
        if "section" in response.lower() or "clause" in response.lower():
            # Extract document references
            pass
        
        return {
            "confidence": confidence_match,
            "citations": citations,
            "has_legal_references": bool(citations),
            "response_length": len(response)
        }