"""
Bill tracking service for AyeSpy.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import joinedload
from database.models import Bill, BillStatusHistory, Representative, Committee, Hearing

logger = logging.getLogger(__name__)


class BillTrackingService:
    """Service for tracking bills and their legislative progress."""
    
    def __init__(self, db_manager):
        """Initialize bill tracking service.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
    
    def search_bills(self, query: str, limit: int = 50) -> List[Dict]:
        """Search bills by text query.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching bills
        """
        try:
            with self.db_manager.get_session() as session:
                bills = session.query(Bill).filter(
                    or_(
                        Bill.title.ilike(f"%{query}%"),
                        Bill.summary.ilike(f"%{query}%"),
                        Bill.bill_number.ilike(f"%{query}%")
                    )
                ).options(
                    joinedload(Bill.sponsor)
                ).order_by(desc(Bill.introduced_date)).limit(limit).all()
                
                return [self._bill_to_dict(bill) for bill in bills]
                
        except Exception as e:
            logger.error(f"Bill search failed: {e}")
            return []
    
    def get_bill(self, bill_identifier: str) -> Optional[Dict]:
        """Get a specific bill by ID or number.
        
        Args:
            bill_identifier: Bill ID, number, or full identifier (e.g., HR1234)
            
        Returns:
            Bill data or None
        """
        try:
            with self.db_manager.get_session() as session:
                # Try to parse the identifier
                bill_type, bill_number = self._parse_bill_identifier(bill_identifier)
                
                if not bill_type or not bill_number:
                    return None
                
                # Get current Congress (you might want to make this configurable)
                current_congress = self._get_current_congress()
                
                bill = session.query(Bill).filter(
                    and_(
                        Bill.congress == current_congress,
                        Bill.bill_type == bill_type,
                        Bill.bill_number == bill_number
                    )
                ).options(
                    joinedload(Bill.sponsor),
                    joinedload(Bill.bill_statuses)
                ).first()
                
                if bill:
                    return self._bill_to_dict(bill, include_statuses=True)
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get bill {bill_identifier}: {e}")
            return None
    
    def get_bill_lifecycle(self, bill_identifier: str) -> Optional[Dict]:
        """Get the complete lifecycle of a bill.
        
        Args:
            bill_identifier: Bill ID or number
            
        Returns:
            Bill lifecycle data or None
        """
        try:
            bill_data = self.get_bill(bill_identifier)
            if not bill_data:
                return None
            
            with self.db_manager.get_session() as session:
                # Get all status changes
                statuses = session.query(BillStatusHistory).filter(
                    BillStatusHistory.bill_id == bill_data['id']
                ).order_by(BillStatusHistory.date).all()
                
                lifecycle = {
                    'bill': bill_data,
                    'statuses': []
                }
                
                for status in statuses:
                    lifecycle['statuses'].append({
                        'date': status.date.strftime('%Y-%m-%d'),
                        'status': status.status,
                        'description': status.description,
                        'action_by': status.action_by,
                        'action_details': status.action_details
                    })
                
                return lifecycle
                
        except Exception as e:
            logger.error(f"Failed to get bill lifecycle for {bill_identifier}: {e}")
            return None
    
    def get_bills_by_status(self, status: str, limit: int = 50) -> List[Dict]:
        """Get bills with a specific status.
        
        Args:
            status: Bill status to filter by
            limit: Maximum results
            
        Returns:
            List of bills with the specified status
        """
        try:
            with self.db_manager.get_session() as session:
                bills = session.query(Bill).filter(
                    Bill.current_status == status
                ).options(
                    joinedload(Bill.sponsor)
                ).order_by(desc(Bill.introduced_date)).limit(limit).all()
                
                return [self._bill_to_dict(bill) for bill in bills]
                
        except Exception as e:
            logger.error(f"Failed to get bills by status {status}: {e}")
            return []
    
    def get_recent_bills(self, days: int = 30, limit: int = 50) -> List[Dict]:
        """Get recently introduced bills.
        
        Args:
            days: Number of days to look back
            limit: Maximum results
            
        Returns:
            List of recent bills
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with self.db_manager.get_session() as session:
                bills = session.query(Bill).filter(
                    Bill.introduced_date >= cutoff_date
                ).options(
                    joinedload(Bill.sponsor)
                ).order_by(desc(Bill.introduced_date)).limit(limit).all()
                
                return [self._bill_to_dict(bill) for bill in bills]
                
        except Exception as e:
            logger.error(f"Failed to get recent bills: {e}")
            return []
    
    def get_bills_by_representative(self, representative_id: int, limit: int = 50) -> List[Dict]:
        """Get bills sponsored by a specific representative.
        
        Args:
            representative_id: Representative ID
            limit: Maximum results
            
        Returns:
            List of sponsored bills
        """
        try:
            with self.db_manager.get_session() as session:
                bills = session.query(Bill).filter(
                    Bill.sponsor_id == representative_id
                ).options(
                    joinedload(Bill.sponsor)
                ).order_by(desc(Bill.introduced_date)).limit(limit).all()
                
                return [self._bill_to_dict(bill) for bill in bills]
                
        except Exception as e:
            logger.error(f"Failed to get bills by representative {representative_id}: {e}")
            return []
    
    def get_bills_by_committee(self, committee_id: int, limit: int = 50) -> List[Dict]:
        """Get bills referred to a specific committee.
        
        Args:
            committee_id: Committee ID
            limit: Maximum results
            
        Returns:
            List of bills in committee
        """
        try:
            with self.db_manager.get_session() as session:
                # This would need to be implemented based on your data model
                # You might need to add a committee_id field to bills or track referrals
                print("[yellow]Committee-based bill filtering not yet implemented.[/yellow]")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get bills by committee {committee_id}: {e}")
            return []
    
    def get_bill_statistics(self) -> Dict[str, Any]:
        """Get statistics about bills in the system.
        
        Returns:
            Dictionary with bill statistics
        """
        try:
            with self.db_manager.get_session() as session:
                # Total bills
                total_bills = session.query(Bill).count()
                
                # Bills by status
                status_counts = session.query(
                    Bill.current_status,
                    func.count(Bill.id)
                ).group_by(Bill.current_status).all()
                
                # Bills by type
                type_counts = session.query(
                    Bill.bill_type,
                    func.count(Bill.id)
                ).group_by(Bill.bill_type).all()
                
                # Recent activity
                recent_bills = session.query(Bill).filter(
                    Bill.introduced_date >= datetime.now() - timedelta(days=7)
                ).count()
                
                # Bills by party
                party_counts = session.query(
                    Representative.party,
                    func.count(Bill.id)
                ).join(Bill, Bill.sponsor_id == Representative.id).group_by(Representative.party).all()
                
                return {
                    'total_bills': total_bills,
                    'recent_bills_7_days': recent_bills,
                    'status_breakdown': dict(status_counts),
                    'type_breakdown': dict(type_counts),
                    'party_breakdown': dict(party_counts)
                }
                
        except Exception as e:
            logger.error(f"Failed to get bill statistics: {e}")
            return {}
    
    def get_bill_timeline(self, bill_identifier: str) -> Optional[List[Dict]]:
        """Get a timeline of events for a specific bill.
        
        Args:
            bill_identifier: Bill ID or number
            
        Returns:
            List of timeline events or None
        """
        try:
            lifecycle = self.get_bill_lifecycle(bill_identifier)
            if not lifecycle:
                return None
            
            timeline = []
            
            # Add bill introduction
            bill = lifecycle['bill']
            timeline.append({
                'date': bill['introduced_date'],
                'event': 'Bill Introduced',
                'description': f"{bill['bill_type'].upper()}{bill['bill_number']} introduced by {bill['sponsor_name']}",
                'type': 'introduction'
            })
            
            # Add status changes
            for status in lifecycle['statuses']:
                timeline.append({
                    'date': status['date'],
                    'event': status['status'].replace('_', ' ').title(),
                    'description': status['description'] or f"Status changed to {status['status']}",
                    'type': 'status_change',
                    'action_by': status['action_by']
                })
            
            # Sort by date
            timeline.sort(key=lambda x: x['date'])
            
            return timeline
            
        except Exception as e:
            logger.error(f"Failed to get bill timeline for {bill_identifier}: {e}")
            return None
    
    def _parse_bill_identifier(self, identifier: str) -> tuple[Optional[str], Optional[str]]:
        """Parse a bill identifier into type and number.
        
        Args:
            identifier: Bill identifier (e.g., HR1234, S.567, etc.)
            
        Returns:
            Tuple of (bill_type, bill_number) or (None, None) if invalid
        """
        if not identifier:
            return None, None
        
        # Remove common prefixes and clean up
        identifier = identifier.upper().strip()
        
        # Handle different formats
        if identifier.startswith('HR'):
            return 'hr', identifier[2:]
        elif identifier.startswith('S'):
            return 's', identifier[1:].lstrip('.')
        elif identifier.startswith('HJR'):
            return 'hjres', identifier[3:]
        elif identifier.startswith('SJR'):
            return 'sjres', identifier[3:]
        elif identifier.startswith('HCR'):
            return 'hconres', identifier[3:]
        elif identifier.startswith('SCR'):
            return 'sconres', identifier[3:]
        else:
            # Try to extract from other formats
            import re
            match = re.match(r'([A-Z]+)[\s.]*(\d+)', identifier)
            if match:
                bill_type = match.group(1).lower()
                bill_number = match.group(2)
                return bill_type, bill_number
        
        return None, None
    
    def _get_current_congress(self) -> int:
        """Get the current Congress number."""
        # This is a simple calculation - you might want to make this configurable
        current_year = datetime.now().year
        congress_start_year = 1789
        congress_number = ((current_year - congress_start_year) // 2) + 1
        return congress_number
    
    def _bill_to_dict(self, bill: Bill, include_statuses: bool = False) -> Dict:
        """Convert a Bill object to a dictionary.
        
        Args:
            bill: Bill object
            include_statuses: Whether to include status history
            
        Returns:
            Dictionary representation of the bill
        """
        bill_dict = {
            'id': bill.id,
            'congress': bill.congress,
            'bill_number': bill.bill_number,
            'bill_type': bill.bill_type,
            'title': bill.title,
            'short_title': bill.short_title,
            'summary': bill.summary,
            'introduced_date': bill.introduced_date.strftime('%Y-%m-%d') if bill.introduced_date else None,
            'current_status': bill.current_status,
            'is_active': bill.is_active,
            'sponsor_name': bill.sponsor.full_name if bill.sponsor else 'Unknown',
            'sponsor_party': bill.sponsor.party if bill.sponsor else None,
            'sponsor_state': bill.sponsor.state if bill.sponsor else None,
            'created_at': bill.created_at.strftime('%Y-%m-%d %H:%M:%S') if bill.created_at else None,
            'updated_at': bill.updated_at.strftime('%Y-%m-%d %H:%M:%S') if bill.updated_at else None
        }
        
        if include_statuses and hasattr(bill, 'bill_statuses'):
            bill_dict['statuses'] = [
                {
                    'date': status.date.strftime('%Y-%m-%d'),
                    'status': status.status,
                    'description': status.description,
                    'action_by': status.action_by
                }
                for status in bill.bill_statuses
            ]
        
        return bill_dict
    
    def get_bill_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics about bill activity.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with analytics data
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with self.db_manager.get_session() as session:
                # Bills introduced in time period
                bills_introduced = session.query(Bill).filter(
                    Bill.introduced_date >= cutoff_date
                ).count()
                
                # Status changes in time period
                status_changes = session.query(BillStatusHistory).filter(
                    BillStatusHistory.date >= cutoff_date
                ).count()
                
                # Most active sponsors
                active_sponsors = session.query(
                    Representative.full_name,
                    Representative.party,
                    func.count(Bill.id)
                ).join(Bill, Bill.sponsor_id == Representative.id).filter(
                    Bill.introduced_date >= cutoff_date
                ).group_by(Representative.id, Representative.full_name, Representative.party).order_by(
                    func.count(Bill.id).desc()
                ).limit(10).all()
                
                # Status distribution
                status_distribution = session.query(
                    Bill.current_status,
                    func.count(Bill.id)
                ).filter(
                    Bill.introduced_date >= cutoff_date
                ).group_by(Bill.current_status).all()
                
                return {
                    'period_days': days,
                    'bills_introduced': bills_introduced,
                    'status_changes': status_changes,
                    'active_sponsors': [
                        {
                            'name': sponsor[0],
                            'party': sponsor[1],
                            'bill_count': sponsor[2]
                        }
                        for sponsor in active_sponsors
                    ],
                    'status_distribution': dict(status_distribution)
                }
                
        except Exception as e:
            logger.error(f"Failed to get bill analytics: {e}")
            return {}
    
    def get_total_bill_count(self) -> int:
        """Get the total number of bills in the database.
        
        Returns:
            Total count of bills
        """
        try:
            with self.db_manager.get_session() as session:
                return session.query(Bill).count()
        except Exception as e:
            logger.error(f"Failed to get total bill count: {e}")
            return 0
    
    def get_bills_paginated(self, page: int = 1, page_size: int = 20) -> List[Dict]:
        """Get bills with pagination.
        
        Args:
            page: Page number (1-based)
            page_size: Number of bills per page
            
        Returns:
            List of bills for the specified page
        """
        try:
            with self.db_manager.get_session() as session:
                offset = (page - 1) * page_size
                
                bills = session.query(Bill).options(
                    joinedload(Bill.sponsor)
                ).order_by(
                    desc(Bill.introduced_date)
                ).offset(offset).limit(page_size).all()
                
                return [self._bill_to_dict(bill) for bill in bills]
                
        except Exception as e:
            logger.error(f"Failed to get paginated bills: {e}")
            return [] 