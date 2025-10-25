"""
Search service for AyeSpy transcript search functionality.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from database.models import TranscriptSegment, Hearing, Committee, Representative
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching congressional transcripts."""
    
    def __init__(self, embedding_service: EmbeddingService, db_manager):
        """Initialize search service.
        
        Args:
            embedding_service: Service for generating and comparing embeddings
            db_manager: Database manager instance
        """
        self.embedding_service = embedding_service
        self.db_manager = db_manager
    
    def search_transcripts(self, query: str, 
                          representative: Optional[str] = None,
                          committee: Optional[str] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          max_results: int = 50,
                          similarity_threshold: float = 0.3) -> List[Dict]:
        """Search transcripts with semantic search and filters.
        
        Args:
            query: Search query text
            representative: Filter by representative name
            committee: Filter by committee name
            start_date: Start date filter
            end_date: End date filter
            max_results: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(query)
            
            # Get transcript segments from database
            segments = self._get_transcript_segments(
                representative=representative,
                committee=committee,
                start_date=start_date,
                end_date=end_date,
                limit=max_results * 2  # Get more for filtering
            )
            
            if not segments:
                logger.info("No transcript segments found matching filters")
                return []
            
            # Extract text and embeddings for similarity calculation
            segment_texts = [segment.text for segment in segments]
            segment_embeddings = []
            
            for segment in segments:
                try:
                    embedding = self.embedding_service.json_to_embedding(segment.text_embedding)
                    segment_embeddings.append(embedding)
                except Exception as e:
                    logger.warning(f"Failed to parse embedding for segment {segment.id}: {e}")
                    # Use zero vector as fallback
                    segment_embeddings.append(
                        self.embedding_service.json_to_embedding("[]")
                    )
            
            # Find most similar segments
            similar_indices = self.embedding_service.find_most_similar(
                query_embedding, segment_embeddings, max_results, similarity_threshold
            )
            
            # Build results with full metadata
            results = []
            for idx, similarity in similar_indices:
                if idx < len(segments):
                    segment = segments[idx]
                    result = self._build_search_result(segment, similarity)
                    results.append(result)
            
            # Sort by similarity score (descending)
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            logger.info(f"Search completed: {len(results)} results found")
            return results
            
        except Exception as e:
            logger.error(f"Transcript search failed: {e}")
            return []
    
    def _get_transcript_segments(self, representative: Optional[str] = None,
                                committee: Optional[str] = None,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None,
                                limit: int = 100) -> List[TranscriptSegment]:
        """Get transcript segments from database with filters.
        
        Args:
            representative: Filter by representative name
            committee: Filter by committee name
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum number of segments
            
        Returns:
            List of transcript segments
        """
        try:
            with self.db_manager.get_session() as session:
                query = session.query(TranscriptSegment).join(
                    Hearing, TranscriptSegment.hearing_id == Hearing.id
                ).join(
                    Committee, Hearing.committee_id == Committee.id
                )
                
                # Apply filters
                if representative:
                    query = query.filter(
                        or_(
                            TranscriptSegment.speaker_name.ilike(f"%{representative}%"),
                            Representative.full_name.ilike(f"%{representative}%")
                        )
                    ).outerjoin(Representative, TranscriptSegment.speaker_id == Representative.id)
                
                if committee:
                    query = query.filter(Committee.name.ilike(f"%{committee}%"))
                
                if start_date:
                    query = query.filter(Hearing.date >= start_date)
                
                if end_date:
                    query = query.filter(Hearing.date <= end_date)
                
                # Order by date (most recent first) and limit results
                query = query.order_by(desc(Hearing.date)).limit(limit)
                
                return query.all()
                
        except Exception as e:
            logger.error(f"Failed to get transcript segments: {e}")
            return []
    
    def _build_search_result(self, segment: TranscriptSegment, similarity: float) -> Dict:
        """Build a search result dictionary from a transcript segment.
        
        Args:
            segment: Transcript segment from database
            similarity: Similarity score
            
        Returns:
            Search result dictionary
        """
        try:
            with self.db_manager.get_session() as session:
                # Get hearing and committee information
                hearing = session.query(Hearing).filter_by(id=segment.hearing_id).first()
                committee = None
                if hearing:
                    committee = session.query(Committee).filter_by(id=hearing.committee_id).first()
                
                # Get representative information if available
                representative = None
                if segment.speaker_id:
                    representative = session.query(Representative).filter_by(id=segment.speaker_id).first()
                
                result = {
                    'id': segment.id,
                    'text': segment.text,
                    'speaker_name': representative.full_name if representative else segment.speaker_name,
                    'speaker_party': representative.party if representative else None,
                    'speaker_state': representative.state if representative else None,
                    'hearing_title': hearing.title if hearing else 'Unknown',
                    'hearing_date': hearing.date.strftime('%Y-%m-%d') if hearing else 'Unknown',
                    'committee_name': committee.name if committee else 'Unknown',
                    'committee_chamber': committee.chamber if committee else 'Unknown',
                    'start_time': segment.start_time,
                    'end_time': segment.end_time,
                    'similarity': similarity,
                    'segment_length': segment.segment_length
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to build search result: {e}")
            # Return basic result if metadata lookup fails
            return {
                'id': segment.id,
                'text': segment.text,
                'speaker_name': segment.speaker_name or 'Unknown',
                'similarity': similarity,
                'segment_length': segment.segment_length
            }
    
    def search_by_keywords(self, keywords: List[str], 
                          max_results: int = 50,
                          use_semantic_search: bool = True) -> List[Dict]:
        """Search transcripts using keyword matching.
        
        Args:
            keywords: List of keywords to search for
            max_results: Maximum number of results
            use_semantic_search: Whether to use semantic search or exact matching
            
        Returns:
            List of search results
        """
        if not keywords:
            return []
        
        try:
            if use_semantic_search:
                # Use semantic search with combined keywords
                query = " ".join(keywords)
                return self.search_transcripts(query, max_results=max_results)
            else:
                # Use exact keyword matching
                return self._keyword_search(keywords, max_results)
                
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []
    
    def _keyword_search(self, keywords: List[str], max_results: int) -> List[Dict]:
        """Perform exact keyword search on transcript segments.
        
        Args:
            keywords: List of keywords
            max_results: Maximum results
            
        Returns:
            List of search results
        """
        try:
            with self.db_manager.get_session() as session:
                # Build keyword filter
                keyword_filters = []
                for keyword in keywords:
                    keyword_filters.append(TranscriptSegment.text.ilike(f"%{keyword}%"))
                
                # Query with OR logic for keywords
                query = session.query(TranscriptSegment).filter(
                    or_(*keyword_filters)
                ).join(
                    Hearing, TranscriptSegment.hearing_id == Hearing.id
                ).order_by(desc(Hearing.date)).limit(max_results)
                
                segments = query.all()
                
                # Build results
                results = []
                for segment in segments:
                    result = self._build_search_result(segment, 1.0)  # Exact match gets max similarity
                    results.append(result)
                
                return results
                
        except Exception as e:
            logger.error(f"Exact keyword search failed: {e}")
            return []
    
    def get_search_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on partial query.
        
        Args:
            partial_query: Partial search query
            limit: Maximum number of suggestions
            
        Returns:
            List of search suggestions
        """
        try:
            with self.db_manager.get_session() as session:
                # Get unique words from transcript segments that start with the partial query
                query = session.query(TranscriptSegment.text).filter(
                    TranscriptSegment.text.ilike(f"%{partial_query}%")
                ).limit(1000)  # Get more segments for better suggestions
                
                segments = query.all()
                
                # Extract words and find suggestions
                suggestions = set()
                for segment in segments:
                    words = segment.text.lower().split()
                    for word in words:
                        if word.startswith(partial_query.lower()) and len(word) > len(partial_query):
                            suggestions.add(word)
                            if len(suggestions) >= limit:
                                break
                    if len(suggestions) >= limit:
                        break
                
                return sorted(list(suggestions))[:limit]
                
        except Exception as e:
            logger.error(f"Failed to get search suggestions: {e}")
            return []
    
    def get_popular_topics(self, days: int = 30, limit: int = 20) -> List[Dict]:
        """Get popular topics from recent transcripts.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of topics
            
        Returns:
            List of popular topics with counts
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with self.db_manager.get_session() as session:
                # Get recent transcript segments
                recent_segments = session.query(TranscriptSegment).join(
                    Hearing, TranscriptSegment.hearing_id == Hearing.id
                ).filter(
                    Hearing.date >= cutoff_date
                ).limit(1000).all()
                
                # Simple topic extraction (can be improved with NLP)
                topics = {}
                for segment in recent_segments:
                    # Extract potential topics (words that appear frequently)
                    words = segment.text.lower().split()
                    for word in words:
                        if len(word) > 4 and word.isalpha():  # Filter short words and non-alphabetic
                            topics[word] = topics.get(word, 0) + 1
                
                # Sort by frequency and return top topics
                sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
                
                return [
                    {'topic': topic, 'count': count}
                    for topic, count in sorted_topics[:limit]
                ]
                
        except Exception as e:
            logger.error(f"Failed to get popular topics: {e}")
            return []
    
    def get_search_statistics(self) -> Dict:
        """Get statistics about the search system.
        
        Returns:
            Dictionary with search statistics
        """
        try:
            with self.db_manager.get_session() as session:
                total_segments = session.query(TranscriptSegment).count()
                total_hearings = session.query(Hearing).count()
                total_representatives = session.query(Representative).count()
                
                # Count segments with embeddings
                segments_with_embeddings = session.query(TranscriptSegment).filter(
                    TranscriptSegment.text_embedding != '[]'
                ).count()
                
                return {
                    'total_transcript_segments': total_segments,
                    'segments_with_embeddings': segments_with_embeddings,
                    'total_hearings': total_hearings,
                    'total_representatives': total_representatives,
                    'embedding_coverage': f"{(segments_with_embeddings / total_segments * 100):.1f}%" if total_segments > 0 else "0%"
                }
                
        except Exception as e:
            logger.error(f"Failed to get search statistics: {e}")
            return {} 