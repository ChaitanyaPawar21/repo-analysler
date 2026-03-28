"""
services/embedding_service.py - Embedding Service
===================================================
Generates vector embeddings for code chunks and stores them in FAISS.
Handles text chunking, embedding generation, and batch processing.
"""

import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np

from core.config import settings
from core.constants import MAX_CHUNK_TOKENS, CHUNK_OVERLAP_TOKENS
from core.logger import get_logger
from db.vector_store import VectorStoreManager

logger = get_logger(__name__)

# Optional OpenAI import
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None


class EmbeddingService:
    """
    Handles code embedding generation and storage.

    Workflow:
        1. Read source files and split into overlapping chunks.
        2. Batch-generate embeddings via OpenAI API.
        3. Store embeddings in the FAISS vector store with metadata.

    Design Notes:
        - Chunking uses a simple character-based splitter with overlap.
        - Batch size is limited to avoid API rate limits.
        - Metadata includes repo_id, file_path, and chunk text for retrieval.
    """

    BATCH_SIZE = 100  # Max chunks per OpenAI embedding API call

    def __init__(self, vector_store: VectorStoreManager):
        self.vector_store = vector_store
        self.client: Optional["AsyncOpenAI"] = None

        if AsyncOpenAI and settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def embed_repository(
        self,
        repo_id: uuid.UUID,
        repo_path: str,
        files: List[Dict[str, Any]],
    ) -> int:
        """
        Generate embeddings for all source files in a repository.

        Args:
            repo_id: UUID of the repository.
            repo_path: Local filesystem path of the cloned repo.
            files: List of file metadata dicts from ParserService.

        Returns:
            Total number of chunks embedded.
        """
        if not self.client:
            logger.warning("Embedding service not configured, skipping embedding generation")
            return 0

        all_chunks = []
        all_metadata = []

        for file_info in files:
            file_path = Path(file_info["path"])
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                logger.warning("Failed to read file for embedding", file=str(file_path), error=str(e))
                continue

            if not content.strip():
                continue

            # Split file content into overlapping chunks
            chunks = self._chunk_text(content)

            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadata.append({
                    "repo_id": str(repo_id),
                    "file_path": file_info["relative_path"],
                    "chunk_index": i,
                    "chunk_text": chunk[:1000],  # Store truncated text for retrieval display
                })

        if not all_chunks:
            logger.info("No content to embed", repo_id=str(repo_id))
            return 0

        # Batch-generate embeddings
        total_embedded = 0
        for batch_start in range(0, len(all_chunks), self.BATCH_SIZE):
            batch_end = batch_start + self.BATCH_SIZE
            chunk_batch = all_chunks[batch_start:batch_end]
            meta_batch = all_metadata[batch_start:batch_end]

            embeddings = await self._generate_embeddings(chunk_batch)
            if embeddings is not None:
                self.vector_store.add_embeddings(embeddings, meta_batch)
                total_embedded += len(chunk_batch)

        # Persist the updated index
        self.vector_store.save()

        logger.info(
            "Repository embedding complete",
            repo_id=str(repo_id),
            total_chunks=total_embedded,
        )
        return total_embedded

    async def _generate_embeddings(self, texts: List[str]) -> Optional[np.ndarray]:
        """
        Generate embeddings for a batch of text strings.

        Returns:
            numpy array of shape (n, dimension) or None on failure.
        """
        try:
            response = await self.client.embeddings.create(
                input=texts,
                model=settings.EMBEDDING_MODEL,
            )
            embeddings = [item.embedding for item in response.data]
            return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e), batch_size=len(texts))
            return None

    def _chunk_text(
        self,
        text: str,
        max_chars: int = MAX_CHUNK_TOKENS * 4,  # Rough chars-per-token estimate
        overlap_chars: int = CHUNK_OVERLAP_TOKENS * 4,
    ) -> List[str]:
        """
        Split text into overlapping chunks for embedding.

        Uses a simple character-based splitter that tries to break on newlines.
        For production, consider using tiktoken for precise token counting.

        Args:
            text: Source code text to chunk.
            max_chars: Maximum characters per chunk.
            overlap_chars: Overlap between consecutive chunks.

        Returns:
            List of text chunks.
        """
        if len(text) <= max_chars:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + max_chars

            # Try to break on a newline for cleaner chunks
            if end < len(text):
                newline_pos = text.rfind("\n", start + max_chars // 2, end)
                if newline_pos != -1:
                    end = newline_pos + 1

            chunks.append(text[start:end])
            start = end - overlap_chars

        return chunks
