"""Embedding utilities based on local sentence-transformers models."""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingService:
    """Reusable embedding service that keeps one model instance in memory."""

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode_texts(self, texts: Iterable[str]) -> np.ndarray:
        """Encode a batch of texts into normalized float32 embeddings."""
        cleaned = [text.strip() if isinstance(text, str) else "" for text in texts]
        embeddings = self.model.encode(
            cleaned,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return np.asarray(embeddings, dtype=np.float32)

    def encode_text(self, text: str) -> np.ndarray:
        """Encode a single text and return a 1D normalized embedding."""
        embeddings = self.encode_texts([text or ""])
        return embeddings[0]


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """Return a singleton embedding service for the process lifecycle."""
    return EmbeddingService()
