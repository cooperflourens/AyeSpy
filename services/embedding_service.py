"""
Embedding service for AyeSpy transcript search functionality.
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import torch

load_dotenv()

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing text embeddings."""
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize embedding service.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name or os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.model = None
        self.embedding_dimension = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dimension}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            # Fallback to a simpler model
            try:
                logger.info("Trying fallback model: all-MiniLM-L6-v2")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embedding_dimension = self.model.get_sentence_embedding_dimension()
                logger.info(f"Fallback model loaded. Embedding dimension: {self.embedding_dimension}")
            except Exception as fallback_error:
                logger.error(f"Fallback model also failed: {fallback_error}")
                raise RuntimeError("No embedding model could be loaded")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array of the embedding
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            # Clean and normalize text
            cleaned_text = self._preprocess_text(text)
            
            # Generate embedding
            embedding = self.model.encode(cleaned_text, convert_to_numpy=True)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(self.embedding_dimension)
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of embeddings (n_texts x embedding_dim)
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            # Clean and normalize texts
            cleaned_texts = [self._preprocess_text(text) for text in texts]
            
            # Generate embeddings in batch
            embeddings = self.model.encode(cleaned_texts, convert_to_numpy=True)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            # Return zero vectors as fallback
            return np.zeros((len(texts), self.embedding_dimension))
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for embedding generation.
        
        Args:
            text: Raw text
            
        Returns:
            Preprocessed text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Truncate if too long (most models have token limits)
        max_length = 512  # Conservative limit
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (-1 to 1)
        """
        try:
            # Normalize vectors
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            
            # Ensure result is in valid range
            return np.clip(similarity, -1.0, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def find_most_similar(self, query_embedding: np.ndarray, 
                          candidate_embeddings: List[np.ndarray],
                          top_k: int = 10,
                          threshold: float = 0.3) -> List[Tuple[int, float]]:
        """Find the most similar embeddings to a query.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        if not candidate_embeddings:
            return []
        
        try:
            similarities = []
            
            for i, candidate in enumerate(candidate_embeddings):
                similarity = self.calculate_similarity(query_embedding, candidate)
                if similarity >= threshold:
                    similarities.append((i, similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Return top_k results
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to find similar embeddings: {e}")
            return []
    
    def embedding_to_json(self, embedding: np.ndarray) -> str:
        """Convert numpy embedding to JSON string for storage.
        
        Args:
            embedding: Numpy array embedding
            
        Returns:
            JSON string representation
        """
        try:
            return json.dumps(embedding.tolist())
        except Exception as e:
            logger.error(f"Failed to convert embedding to JSON: {e}")
            return "[]"
    
    def json_to_embedding(self, json_string: str) -> np.ndarray:
        """Convert JSON string back to numpy embedding.
        
        Args:
            json_string: JSON string representation
            
        Returns:
            Numpy array embedding
        """
        try:
            embedding_list = json.loads(json_string)
            return np.array(embedding_list, dtype=np.float32)
        except Exception as e:
            logger.error(f"Failed to convert JSON to embedding: {e}")
            return np.zeros(self.embedding_dimension)
    
    def update_transcript_embeddings(self, transcript_segments: List[Dict]) -> List[Dict]:
        """Update transcript segments with their embeddings.
        
        Args:
            transcript_segments: List of transcript segment dictionaries
            
        Returns:
            Updated segments with embeddings
        """
        if not transcript_segments:
            return []
        
        try:
            # Extract texts for batch processing
            texts = [segment.get('text', '') for segment in transcript_segments]
            
            # Generate embeddings in batch
            embeddings = self.generate_embeddings_batch(texts)
            
            # Update segments with embeddings
            updated_segments = []
            for i, segment in enumerate(transcript_segments):
                segment_copy = segment.copy()
                segment_copy['text_embedding'] = self.embedding_to_json(embeddings[i])
                updated_segments.append(segment_copy)
            
            logger.info(f"Generated embeddings for {len(transcript_segments)} transcript segments")
            return updated_segments
            
        except Exception as e:
            logger.error(f"Failed to update transcript embeddings: {e}")
            return transcript_segments
    
    def get_model_info(self) -> Dict[str, any]:
        """Get information about the loaded embedding model.
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dimension,
            'is_loaded': self.model is not None,
            'device': str(self.model.device) if self.model else None
        }
    
    def optimize_for_search(self, embeddings: List[np.ndarray]) -> np.ndarray:
        """Optimize embeddings for faster similarity search.
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            Optimized embeddings array
        """
        if not embeddings:
            return np.array([])
        
        try:
            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Normalize all embeddings for faster cosine similarity
            norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Avoid division by zero
            normalized_embeddings = embeddings_array / norms
            
            return normalized_embeddings
            
        except Exception as e:
            logger.error(f"Failed to optimize embeddings: {e}")
            return np.array(embeddings)
    
    def semantic_search(self, query: str, 
                       candidate_texts: List[str],
                       top_k: int = 10,
                       threshold: float = 0.3) -> List[Tuple[int, float, str]]:
        """Perform semantic search on a list of texts.
        
        Args:
            query: Search query
            candidate_texts: List of candidate texts to search
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of (index, similarity_score, text) tuples, sorted by similarity
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Generate embeddings for candidate texts
            candidate_embeddings = self.generate_embeddings_batch(candidate_texts)
            
            # Find most similar
            similar_indices = self.find_most_similar(
                query_embedding, candidate_embeddings, top_k, threshold
            )
            
            # Return results with text
            results = []
            for idx, similarity in similar_indices:
                if idx < len(candidate_texts):
                    results.append((idx, similarity, candidate_texts[idx]))
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return [] 