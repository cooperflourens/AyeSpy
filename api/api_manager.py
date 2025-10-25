"""
API Manager for coordinating between different congressional data sources.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .congress_api import CongressAPI
from .govinfo_api import GovInfoAPI
from database.connection import get_db_manager
from database.models import (
    Representative, Committee, Bill, BillStatusHistory, 
    Hearing, TranscriptSegment, Vote, DataUpdateLog
)

logger = logging.getLogger(__name__)


class APIManager:
    """Manages API interactions and data synchronization."""
    
    def __init__(self):
        """Initialize API manager with all available APIs."""
        self.congress_api = CongressAPI()
        self.govinfo_api = GovInfoAPI()
        self.db_manager = get_db_manager()
        
        # Track current Congress
        self.current_congress = self.congress_api.get_current_congress()
        logger.info(f"Current Congress: {self.current_congress}")
    
    def sync_current_congress_data(self, force: bool = False) -> Dict[str, Any]:
        """Synchronize all data for the current Congress.
        
        Args:
            force: Force update even if recently updated
            
        Returns:
            Dictionary with sync results
        """
        logger.info(f"Starting data synchronization for {self.current_congress}th Congress")
        
        results = {
            'representatives': {'added': 0, 'updated': 0, 'errors': 0},
            'committees': {'added': 0, 'updated': 0, 'errors': 0},
            'bills': {'added': 0, 'updated': 0, 'errors': 0},
            'hearings': {'added': 0, 'updated': 0, 'errors': 0},
            'transcripts': {'added': 0, 'updated': 0, 'errors': 0},
            'votes': {'added': 0, 'updated': 0, 'errors': 0}
        }
        
        try:
            # Start update log
            update_log = DataUpdateLog(
                update_type='full_sync',
                status='in_progress',
                started_at=datetime.now()
            )
            
            with self.db_manager.get_session() as session:
                session.add(update_log)
                session.commit()
                update_log_id = update_log.id
            
            # Sync representatives
            results['representatives'] = self._sync_representatives()
            
            # Sync committees
            results['committees'] = self._sync_committees()
            
            # Sync bills
            results['bills'] = self._sync_bills()
            
            # Sync hearings
            results['hearings'] = self._sync_hearings()
            
            # Sync transcripts (this will take time)
            results['transcripts'] = self._sync_transcripts()
            
            # Sync votes
            results['votes'] = self._sync_votes()
            
            # Update log
            with self.db_manager.get_session() as session:
                update_log = session.query(DataUpdateLog).filter_by(id=update_log_id).first()
                if update_log:
                    update_log.status = 'success'
                    update_log.completed_at = datetime.now()
                    update_log.duration_seconds = (update_log.completed_at - update_log.started_at).total_seconds()
                    update_log.records_processed = sum(r['added'] + r['updated'] for r in results.values())
                    update_log.records_added = sum(r['added'] for r in results.values())
                    update_log.records_updated = sum(r['updated'] for r in results.values())
                    session.commit()
            
            logger.info("Data synchronization completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Data synchronization failed: {e}")
            
            # Update log with error
            try:
                with self.db_manager.get_session() as session:
                    update_log = session.query(DataUpdateLog).filter_by(id=update_log_id).first()
                    if update_log:
                        update_log.status = 'failed'
                        update_log.completed_at = datetime.now()
                        update_log.duration_seconds = (update_log.completed_at - update_log.started_at).total_seconds()
                        update_log.error_message = str(e)
                        session.commit()
            except Exception as log_error:
                logger.error(f"Failed to update error log: {log_error}")
            
            return results
    
    def _sync_representatives(self) -> Dict[str, int]:
        """Synchronize representative data."""
        logger.info("Syncing representatives...")
        
        results = {'added': 0, 'updated': 0, 'errors': 0}
        
        try:
            # Get representatives from both chambers
            for chamber in ['house', 'senate']:
                try:
                    reps = self.congress_api.get_representatives(self.current_congress, chamber)
                    
                    with self.db_manager.get_session() as session:
                        for rep_data in reps:
                            try:
                                # Check if representative exists
                                existing = session.query(Representative).filter_by(
                                    bioguide_id=rep_data['bioguide_id']
                                ).first()
                                
                                if existing:
                                    # Update existing
                                    for key, value in rep_data.items():
                                        if hasattr(existing, key) and value is not None:
                                            setattr(existing, key, value)
                                    existing.updated_at = datetime.now()
                                    results['updated'] += 1
                                else:
                                    # Create new
                                    rep = Representative(**rep_data)
                                    session.add(rep)
                                    results['added'] += 1
                                
                            except Exception as e:
                                logger.error(f"Error processing representative {rep_data.get('full_name', 'Unknown')}: {e}")
                                results['errors'] += 1
                        
                        session.commit()
                        
                except Exception as e:
                    logger.error(f"Error syncing {chamber} representatives: {e}")
                    results['errors'] += 1
            
            logger.info(f"Representatives sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Representatives sync failed: {e}")
            results['errors'] += 1
            return results
    
    def _sync_committees(self) -> Dict[str, int]:
        """Synchronize committee data."""
        logger.info("Syncing committees...")
        
        results = {'added': 0, 'updated': 0, 'errors': 0}
        
        try:
            committees = self.congress_api.get_committees(self.current_congress)
            
            with self.db_manager.get_session() as session:
                for committee_data in committees:
                    try:
                        # Check if committee exists
                        existing = session.query(Committee).filter_by(
                            congress_id=committee_data['congress_id']
                        ).first()
                        
                        if existing:
                            # Update existing
                            for key, value in committee_data.items():
                                if hasattr(existing, key) and value is not None:
                                    setattr(existing, key, value)
                            existing.updated_at = datetime.now()
                            results['updated'] += 1
                        else:
                            # Create new
                            committee = Committee(**committee_data)
                            session.add(committee)
                            results['added'] += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing committee {committee_data.get('name', 'Unknown')}: {e}")
                        results['errors'] += 1
                
                session.commit()
            
            logger.info(f"Committees sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Committees sync failed: {e}")
            results['errors'] += 1
            return results
    
    def _sync_bills(self) -> Dict[str, int]:
        """Synchronize bill data."""
        logger.info("Syncing bills...")
        
        results = {'added': 0, 'updated': 0, 'errors': 0}
        
        try:
            # Get bills from both chambers
            bill_types = ['hr', 's', 'hjres', 'sjres', 'hconres', 'sconres']
            
            for bill_type in bill_types:
                try:
                    bills = self.congress_api.get_bills(self.current_congress, bill_type, limit=1000)
                    
                    with self.db_manager.get_session() as session:
                        for bill_data in bills:
                            try:
                                # Get detailed bill information
                                detailed_bill = self.congress_api.get_bill_details(
                                    self.current_congress, 
                                    bill_data['bill_type'], 
                                    int(bill_data['bill_number'])
                                )
                                
                                if detailed_bill:
                                    # Merge basic and detailed data
                                    bill_data.update(detailed_bill)
                                
                                # Check if bill exists
                                existing = session.query(Bill).filter_by(
                                    congress=bill_data['congress'],
                                    bill_number=bill_data['bill_number'],
                                    bill_type=bill_data['bill_type']
                                ).first()
                                
                                if existing:
                                    # Update existing
                                    for key, value in bill_data.items():
                                        if hasattr(existing, key) and value is not None:
                                            setattr(existing, key, value)
                                    existing.updated_at = datetime.now()
                                    results['updated'] += 1
                                    bill_obj = existing
                                else:
                                    # Create new - filter out extra fields
                                    bill_fields = {k: v for k, v in bill_data.items() 
                                                 if hasattr(Bill, k) and v is not None}
                                    bill_obj = Bill(**bill_fields)
                                    session.add(bill_obj)
                                    results['added'] += 1
                                
                                # Sync bill status history if we have detailed data
                                if detailed_bill and 'actions' in detailed_bill:
                                    self._sync_bill_status_history(session, bill_obj, detailed_bill['actions'])
                                
                                # Handle sponsor relationship
                                if detailed_bill and 'sponsor_bioguide_id' in detailed_bill and detailed_bill['sponsor_bioguide_id']:
                                    sponsor = session.query(Representative).filter_by(
                                        bioguide_id=detailed_bill['sponsor_bioguide_id']
                                    ).first()
                                    if sponsor:
                                        bill_obj.sponsor_id = sponsor.id
                                
                            except Exception as e:
                                logger.error(f"Error processing bill {bill_data.get('title', 'Unknown')}: {e}")
                                results['errors'] += 1
                        
                        session.commit()
                        
                except Exception as e:
                    logger.error(f"Error syncing {bill_type} bills: {e}")
                    results['errors'] += 1
            
            logger.info(f"Bills sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Bills sync failed: {e}")
            results['errors'] += 1
            return results
    
    def _sync_hearings(self) -> Dict[str, int]:
        """Synchronize hearing data."""
        logger.info("Syncing hearings...")
        
        results = {'added': 0, 'updated': 0, 'errors': 0}
        
        try:
            hearings = self.govinfo_api.get_congressional_hearings(self.current_congress, limit=1000)
            
            with self.db_manager.get_session() as session:
                for hearing_data in hearings:
                    try:
                        # Check if hearing exists by title and date
                        existing = session.query(Hearing).filter_by(
                            title=hearing_data.get('title'),
                            date=hearing_data.get('date')
                        ).first()
                        
                        if existing:
                            # Update existing
                            for key, value in hearing_data.items():
                                if hasattr(existing, key) and value is not None:
                                    setattr(existing, key, value)
                            existing.updated_at = datetime.now()
                            results['updated'] += 1
                        else:
                            # Create new - filter out extra fields
                            hearing_fields = {k: v for k, v in hearing_data.items() 
                                           if hasattr(Hearing, k) and v is not None}
                            hearing = Hearing(**hearing_fields)
                            session.add(hearing)
                            results['added'] += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing hearing {hearing_data.get('title', 'Unknown')}: {e}")
                        results['errors'] += 1
                
                session.commit()
            
            logger.info(f"Hearings sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Hearings sync failed: {e}")
            results['errors'] += 1
            return results
    
    def _sync_transcripts(self) -> Dict[str, int]:
        """Synchronize transcript data. This is resource-intensive."""
        logger.info("Syncing transcripts...")
        
        results = {'added': 0, 'updated': 0, 'errors': 0}
        
        try:
            # Get hearings that don't have transcripts yet
            with self.db_manager.get_session() as session:
                hearings_without_transcripts = session.query(Hearing).filter(
                    ~Hearing.transcript_segments.any()
                ).limit(50).all()  # Process in batches
            
            for hearing in hearings_without_transcripts:
                try:
                    # Get transcript from GovInfo
                    transcript_data = self.govinfo_api.get_hearing_transcript(hearing.package_id)
                    
                    if transcript_data and transcript_data.get('transcript_text'):
                        # Process transcript into segments
                        segments = self._process_transcript_into_segments(
                            hearing.id, 
                            transcript_data['transcript_text']
                        )
                        
                        # Add segments to database
                        with self.db_manager.get_session() as session:
                            for segment_data in segments:
                                segment = TranscriptSegment(**segment_data)
                                session.add(segment)
                            
                            session.commit()
                            results['added'] += len(segments)
                        
                        logger.info(f"Processed transcript for hearing {hearing.id}: {len(segments)} segments")
                    
                except Exception as e:
                    logger.error(f"Error processing transcript for hearing {hearing.id}: {e}")
                    results['errors'] += 1
            
            logger.info(f"Transcripts sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Transcripts sync failed: {e}")
            results['errors'] += 1
            return results
    
    def _sync_votes(self) -> Dict[str, int]:
        """Synchronize voting data."""
        logger.info("Syncing votes...")
        
        results = {'added': 0, 'updated': 0, 'errors': 0}
        
        try:
            # Get votes from both chambers
            for chamber in ['house', 'senate']:
                for session_num in [1, 2]:  # Most Congresses have 2 sessions
                    try:
                        votes = self.congress_api.get_votes(self.current_congress, chamber, session_num)
                        
                        with self.db_manager.get_session() as session:
                            for vote_data in votes:
                                try:
                                    # Get detailed vote information
                                    detailed_vote = self.congress_api.get_vote_details(
                                        self.current_congress, chamber, session_num, vote_data['roll_call']
                                    )
                                    
                                    if detailed_vote:
                                        # Process individual vote positions
                                        for position in detailed_vote.get('positions', []):
                                            try:
                                                # Check if vote exists
                                                existing = session.query(Vote).filter_by(
                                                    bill_id=position.get('bill_id'),
                                                    representative_id=position.get('member_id'),
                                                    roll_call_number=vote_data['roll_call']
                                                ).first()
                                                
                                                if not existing:
                                                    # Create new vote record
                                                    vote = Vote(
                                                        bill_id=position.get('bill_id'),
                                                        representative_id=position.get('member_id'),
                                                        vote_position=position.get('vote_position'),
                                                        vote_date=vote_data['vote_date'],
                                                        roll_call_number=vote_data['roll_call'],
                                                        chamber=chamber
                                                    )
                                                    session.add(vote)
                                                    results['added'] += 1
                                                
                                            except Exception as e:
                                                logger.error(f"Error processing vote position: {e}")
                                                results['errors'] += 1
                                        
                                        session.commit()
                                        
                                except Exception as e:
                                    logger.error(f"Error processing vote {vote_data.get('roll_call', 'Unknown')}: {e}")
                                    results['errors'] += 1
                        
                    except Exception as e:
                        logger.error(f"Error syncing {chamber} session {session_num} votes: {e}")
                        results['errors'] += 1
            
            logger.info(f"Votes sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Votes sync failed: {e}")
            results['errors'] += 1
            return results
    
    def _process_transcript_into_segments(self, hearing_id: int, transcript_text: str, 
                                        max_segment_length: int = 500) -> List[Dict]:
        """Process transcript text into searchable segments.
        
        Args:
            hearing_id: Database hearing ID
            transcript_text: Raw transcript text
            max_segment_length: Maximum characters per segment
            
        Returns:
            List of segment data dictionaries
        """
        segments = []
        
        # Simple text segmentation (can be improved with NLP)
        lines = transcript_text.split('\n')
        current_segment = ""
        current_speaker = "Unknown"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line indicates a new speaker
            if ':' in line and len(line.split(':')[0]) < 50:
                # Save previous segment
                if current_segment:
                    segments.append({
                        'hearing_id': hearing_id,
                        'speaker_name': current_speaker,
                        'text': current_segment.strip(),
                        'segment_length': len(current_segment),
                        'text_embedding': '[]'  # Will be populated by embedding service
                    })
                
                # Start new segment
                speaker_part = line.split(':')[0]
                current_speaker = speaker_part.strip()
                current_segment = line.split(':', 1)[1] if ':' in line else line
            else:
                # Add to current segment
                if current_segment:
                    current_segment += " " + line
                else:
                    current_segment = line
            
            # Check if segment is too long
            if len(current_segment) > max_segment_length:
                # Split long segment
                words = current_segment.split()
                temp_segment = ""
                
                for word in words:
                    if len(temp_segment + " " + word) <= max_segment_length:
                        temp_segment += (" " + word) if temp_segment else word
                    else:
                        # Save current segment
                        if temp_segment:
                            segments.append({
                                'hearing_id': hearing_id,
                                'speaker_name': current_speaker,
                                'text': temp_segment.strip(),
                                'segment_length': len(temp_segment),
                                'text_embedding': '[]'
                            })
                        
                        # Start new segment
                        temp_segment = word
                
                current_segment = temp_segment
        
        # Add final segment
        if current_segment:
            segments.append({
                'hearing_id': hearing_id,
                'speaker_name': current_speaker,
                'text': current_segment.strip(),
                'segment_length': len(current_segment),
                'text_embedding': '[]'
            })
        
        return segments
    
    def get_recent_updates(self, hours: int = 24) -> Dict[str, Any]:
        """Get recently updated data.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary of recent updates
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.db_manager.get_session() as session:
            recent_bills = session.query(Bill).filter(
                Bill.updated_at >= cutoff_time
            ).order_by(Bill.updated_at.desc()).limit(20).all()
            
            recent_hearings = session.query(Hearing).filter(
                Hearing.updated_at >= cutoff_time
            ).order_by(Hearing.updated_at.desc()).limit(20).all()
            
            recent_votes = session.query(Vote).filter(
                Vote.created_at >= cutoff_time
            ).order_by(Vote.created_at.desc()).limit(20).all()
        
        return {
            'bills': recent_bills,
            'hearings': recent_hearings,
            'votes': recent_votes,
            'cutoff_time': cutoff_time
        }
    
    def search_transcripts(self, query: str, limit: int = 50, 
                          representative: Optional[str] = None,
                          committee: Optional[str] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[Dict]:
        """Search transcripts with various filters.
        
        Args:
            query: Search query
            limit: Maximum results
            representative: Filter by representative name
            committee: Filter by committee
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            List of matching transcript segments
        """
        # This will be implemented with the embedding search service
        # For now, return empty list
        logger.info(f"Transcript search requested: {query}")
        return []
    
    def _sync_bill_status_history(self, session, bill_obj, actions):
        """Sync bill status history from API actions data.
        
        Args:
            session: Database session
            bill_obj: Bill object
            actions: List of action dictionaries from API
        """
        try:
            from database.models import BillStatusHistory
            from datetime import datetime
            
            for action in actions:
                if not isinstance(action, dict):
                    continue
                    
                # Check if status history entry exists
                existing = session.query(BillStatusHistory).filter_by(
                    bill_id=bill_obj.id,
                    status=action.get('text', ''),
                    date=action.get('action_date')
                ).first()
                
                if not existing and action.get('action_date') and action.get('text'):
                    # Create new status history entry
                    try:
                        action_date = datetime.fromisoformat(action['action_date'].replace('Z', '+00:00'))
                    except:
                        action_date = datetime.now()
                    
                    status_history = BillStatusHistory(
                        bill_id=bill_obj.id,
                        status=action['text'],
                        date=action_date,
                        description=action.get('text'),
                        action_by=action.get('action_by'),
                        action_details=f"Chamber: {action.get('chamber', 'Unknown')}, Code: {action.get('action_code', 'Unknown')}"
                    )
                    session.add(status_history)
                    
        except Exception as e:
            logger.error(f"Failed to sync bill status history: {e}") 