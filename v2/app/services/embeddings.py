import logging
from typing import List, Tuple

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore
    np = None  # type: ignore


logger = logging.getLogger(__name__)


class EmbeddingService:
    """Local embedding service using sentence-transformers (MiniLM)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.available = False
        if SentenceTransformer is not None:
            try:
                self.model = SentenceTransformer(self.model_name)
                self.available = True
            except Exception as e:  # pragma: no cover
                logger.warning(f"Failed to load embedding model {self.model_name}: {e}")

    def is_available(self) -> bool:
        return self.available and self.model is not None and np is not None

    def embed(self, text: str):
        if not self.is_available():
            return None
        vec = self.model.encode(text or "", normalize_embeddings=True)
        return vec

    def embed_texts(self, texts: List[str]):
        if not self.is_available():
            return None
        vecs = self.model.encode(texts, normalize_embeddings=True)
        return vecs

    def rank(self, query: str, texts: List[str], top_k: int = 20) -> List[Tuple[int, float]]:
        if not self.is_available() or not texts:
            return []
        q = self.embed(query or "")
        m = self.embed_texts(texts)
        if q is None or m is None:
            return []
        # cosine similarity since embeddings are normalized: dot product
        sims = (m @ q)  # type: ignore
        # argsort descending
        indices = sims.argsort()[::-1][:top_k]
        return [(int(i), float(sims[i])) for i in indices]


