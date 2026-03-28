"""
services/ai_service.py - AI / LLM Service
==========================================
Handles interactions with the LLM for codebase Q&A and summarization.
Integrates with the vector store for Retrieval-Augmented Generation (RAG).
"""

import uuid
from typing import List, Optional

from core.config import settings
from core.logger import get_logger
from db.vector_store import VectorStoreManager
from schemas.chat_schema import ChatResponse, ChatSource

logger = get_logger(__name__)

# Optional OpenAI import — gracefully handle missing dependency
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None
    logger.warning("OpenAI package not installed. AI features will be unavailable.")


class AIService:
    """
    Provides AI-powered chat and summarization over analyzed codebases.

    Uses Retrieval-Augmented Generation (RAG):
        1. Convert user query to embedding via OpenAI.
        2. Search FAISS vector store for relevant code chunks.
        3. Build a context-enriched prompt with retrieved chunks.
        4. Send to LLM for response generation.
        5. Return response with source attributions.

    Migration Note:
        This service is stateless and can be called from both
        FastAPI endpoints and Celery tasks without modification.
    """

    def __init__(self, vector_store: VectorStoreManager):
        self.vector_store = vector_store
        self.client: Optional["AsyncOpenAI"] = None

        if AsyncOpenAI and settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def chat(
        self,
        repo_id: uuid.UUID,
        user_message: str,
        conversation_history: Optional[List[dict]] = None,
    ) -> ChatResponse:
        """
        Process a chat message against a repository's codebase.

        Args:
            repo_id: The repository to query.
            user_message: The user's question or prompt.
            conversation_history: Optional prior messages for multi-turn context.

        Returns:
            ChatResponse with AI answer and source attributions.
        """
        if not self.client:
            raise RuntimeError(
                "AI service not configured. Set OPENAI_API_KEY in environment."
            )

        # Step 1: Generate query embedding
        query_embedding = await self._get_embedding(user_message)

        # Step 2: Search vector store for relevant code chunks
        import numpy as np
        query_vector = np.array([query_embedding], dtype=np.float32)
        results = self.vector_store.search(query_vector, top_k=5)

        # Filter results to the target repository
        repo_results = [
            (meta, score) for meta, score in results
            if meta.get("repo_id") == str(repo_id)
        ]

        # Step 3: Build context from retrieved chunks
        context_chunks = []
        sources = []
        for meta, score in repo_results:
            context_chunks.append(
                f"File: {meta.get('file_path', 'unknown')}\n"
                f"```\n{meta.get('chunk_text', '')}\n```"
            )
            sources.append(ChatSource(
                file_path=meta.get("file_path", "unknown"),
                snippet=meta.get("chunk_text", "")[:500],
                relevance_score=round(score, 4),
            ))

        context = "\n\n".join(context_chunks) if context_chunks else "No relevant code found."

        # Step 4: Build prompt and call LLM
        system_prompt = (
            "You are an expert code analyst. Answer questions about the codebase "
            "based on the provided code context. Be specific, reference file names "
            "and function names. If the context doesn't contain enough information, "
            "say so clearly."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Code Context:\n{context}\n\nQuestion: {user_message}"},
        ]

        # Include conversation history if provided
        if conversation_history:
            messages = [messages[0]] + conversation_history + [messages[-1]]

        response = await self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2000,
        )

        ai_message = response.choices[0].message.content

        return ChatResponse(
            conversation_id=uuid.uuid4(),
            message=ai_message,
            sources=sources,
        )

    async def summarize_repository(self, repo_id: uuid.UUID, files: list[dict]) -> str:
        """
        Generate an AI summary of the repository based on its structure.

        Args:
            repo_id: Repository UUID.
            files: List of file metadata dicts.

        Returns:
            A concise summary of the repository.
        """
        if not self.client:
            return "AI summarization unavailable. Configure OPENAI_API_KEY."

        # Build a structural overview
        file_list = "\n".join(
            f"- {f['relative_path']} ({f['language']}, {f.get('line_count', 0)} lines)"
            for f in files[:50]  # Limit to avoid token overflow
        )

        prompt = (
            f"Analyze this repository structure and provide a concise summary:\n\n"
            f"Files ({len(files)} total, showing first 50):\n{file_list}\n\n"
            f"Provide: 1) What the project does, 2) Tech stack, "
            f"3) Architecture pattern, 4) Key components."
        )

        response = await self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
        )

        return response.choices[0].message.content

    async def _get_embedding(self, text: str) -> List[float]:
        """Generate an embedding vector for the given text using OpenAI."""
        response = await self.client.embeddings.create(
            input=text,
            model=settings.EMBEDDING_MODEL,
        )
        return response.data[0].embedding
