"""
db/vector_store.py - FAISS Vector Store Manager
================================================
Manages FAISS index for storing and querying code embeddings.
Provides methods to add, search, and persist vector indices.
"""

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

from core.config import settings
from core.constants import DEFAULT_TOP_K
from core.logger import get_logger

logger = get_logger(__name__)

# FAISS is an optional heavy dependency; handle import gracefully
try:
    import faiss
except ImportError:
    faiss = None
    logger.warning("FAISS not installed. Vector search will be unavailable.")


class VectorStoreManager:
    """
    Manages a FAISS flat index for code-chunk embeddings.

    Design Notes:
        - Uses IndexFlatIP (inner product) for cosine similarity on normalized vectors.
        - Index is persisted to disk and loaded on startup.
        - Thread-safe for reads; writes should be serialized (single-writer pattern).
        - Can be swapped for a managed vector DB (Pinecone, Weaviate) later.
    """

    def __init__(self, dimension: int = settings.FAISS_DIMENSION):
        self.dimension = dimension
        self.index: Optional["faiss.IndexFlatIP"] = None
        self.index_path = Path(settings.FAISS_INDEX_PATH)
        # Maps FAISS internal IDs → application metadata (repo_id, file_path, chunk_id)
        self.id_map: dict[int, dict] = {}

    def initialize(self) -> None:
        """
        Initialize or load existing FAISS index from disk.
        Called once during application startup.
        """
        if faiss is None:
            logger.error("Cannot initialize vector store: faiss not installed")
            return

        index_file = self.index_path / "index.faiss"

        if index_file.exists():
            self.index = faiss.read_index(str(index_file))
            logger.info(
                "Loaded existing FAISS index",
                total_vectors=self.index.ntotal,
                dimension=self.dimension,
            )
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.index_path.mkdir(parents=True, exist_ok=True)
            logger.info(
                "Created new FAISS index",
                dimension=self.dimension,
            )

    def add_embeddings(
        self,
        embeddings: np.ndarray,
        metadata: List[dict],
    ) -> None:
        """
        Add embedding vectors to the FAISS index.

        Args:
            embeddings: numpy array of shape (n, dimension), L2-normalized.
            metadata: list of dicts with keys like repo_id, file_path, chunk_text.
        """
        if self.index is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension {embeddings.shape[1]} != expected {self.dimension}"
            )

        # Normalize vectors for cosine similarity via inner product
        faiss.normalize_L2(embeddings)

        start_id = self.index.ntotal
        self.index.add(embeddings)

        # Map internal FAISS IDs to application metadata
        for i, meta in enumerate(metadata):
            self.id_map[start_id + i] = meta

        logger.info(
            "Added embeddings to vector store",
            count=len(metadata),
            total_vectors=self.index.ntotal,
        )

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = DEFAULT_TOP_K,
    ) -> List[Tuple[dict, float]]:
        """
        Search for the most similar vectors to the query.

        Args:
            query_embedding: numpy array of shape (1, dimension).
            top_k: number of results to return.

        Returns:
            List of (metadata_dict, similarity_score) tuples, sorted by relevance.
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Vector store is empty, returning no results")
            return []

        # Normalize query vector
        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue  # FAISS returns -1 for padding when fewer results exist
            meta = self.id_map.get(int(idx), {"id": int(idx)})
            results.append((meta, float(score)))

        return results

    def save(self) -> None:
        """Persist the FAISS index to disk."""
        if self.index is None:
            return

        self.index_path.mkdir(parents=True, exist_ok=True)
        index_file = self.index_path / "index.faiss"
        faiss.write_index(self.index, str(index_file))
        logger.info("FAISS index saved to disk", path=str(index_file))

    def reset(self) -> None:
        """Clear the index and metadata (useful for testing)."""
        if faiss is not None:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.id_map.clear()
            logger.info("Vector store reset")

    @property
    def total_vectors(self) -> int:
        """Return the total number of vectors in the index."""
        return self.index.ntotal if self.index else 0
