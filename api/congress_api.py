"""
Congress.gov API integration for AyeSpy.
Provides access to bills, representatives, and voting data.
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import time

load_dotenv()

logger = logging.getLogger(__name__)


class CongressAPI:
    """Congress.gov API client for retrieving congressional data."""
    
    BASE_URL = "https://api.congress.gov/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Congress API client.
        
        Args:
            api_key: Congress.gov API key. If None, uses environment variable.
        """
        self.api_key = api_key or os.getenv('CONGRESS_API_KEY')
        if not self.api_key:
            logger.warning("No Congress.gov API key provided. Some endpoints may not work.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AyeSpy/1.0 (Congressional Transparency Platform)',
            'Accept': 'application/json'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a rate-limited request to the Congress API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            API response data or None if failed
        """
        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        url = f"{self.BASE_URL}{endpoint}"
        if params is None:
            params = {}
        
        if self.api_key:
            params['api_key'] = self.api_key
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("Rate limit exceeded, waiting...")
                time.sleep(60)  # Wait 1 minute
                return self._make_request(endpoint, params)
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def get_current_congress(self) -> int:
        """Get the current Congress number."""
        try:
            # Each Congress lasts 2 years, starting in odd years
            current_year = datetime.now().year
            congress_start_year = 1789  # First Congress
            congress_number = ((current_year - congress_start_year) // 2) + 1
            return congress_number
        except Exception as e:
            logger.error(f"Failed to determine current Congress: {e}")
            return 119  # Fallback to 119th Congress (current)
    
    def get_bills(self, congress: int, bill_type: str = "hr", limit: int = 100) -> List[Dict]:
        """Get bills from a specific Congress.
        
        Args:
            congress: Congress number
            bill_type: Type of bill (hr, s, hjres, sjres, etc.)
            limit: Maximum number of bills to return
            
        Returns:
            List of bill data dictionaries
        """
        endpoint = f"/bill/{congress}/{bill_type}"
        params = {'limit': limit}
        
        data = self._make_request(endpoint, params)
        if not data:
            return []
        
        bills = []
        for bill in data.get('bills', []):
            bill_data = {
                'congress': congress,
                'bill_number': bill.get('number'),
                'bill_type': bill_type,
                'title': bill.get('title'),
                'short_title': bill.get('shortTitle'),
                'summary': bill.get('summary'),
                'introduced_date': bill.get('introducedDate'),
                'sponsor': bill.get('sponsor'),
                'current_status': bill.get('latestAction', {}).get('actionBy'),
                'url': bill.get('url'),
                'api_url': bill.get('apiUrl')
            }
            bills.append(bill_data)
        
        return bills
    
    def get_bill_details(self, congress: int, bill_type: str, bill_number: int) -> Optional[Dict]:
        """Get detailed information about a specific bill.
        
        Args:
            congress: Congress number
            bill_type: Type of bill
            bill_number: Bill number
            
        Returns:
            Detailed bill data or None
        """
        endpoint = f"/bill/{congress}/{bill_type}/{bill_number}"
        
        data = self._make_request(endpoint)
        if not data:
            return None
        
        bill = data.get('bill', {})
        
        # Get actions (status changes)
        actions = []
        actions_data = bill.get('actions', [])
        if isinstance(actions_data, list):
            for action in actions_data:
                if isinstance(action, dict):
                    action_data = {
                        'action_date': action.get('actionDate'),
                        'text': action.get('text'),
                        'action_by': action.get('actionBy'),
                        'chamber': action.get('chamber'),
                        'action_code': action.get('actionCode')
                    }
                    actions.append(action_data)
        
        # Get subjects
        subjects = [subject.get('name') for subject in bill.get('subjects', [])]
        
        # Extract sponsor information
        sponsor_data = bill.get('sponsor', {})
        sponsor_id = None
        if sponsor_data and isinstance(sponsor_data, dict):
            sponsor_id = sponsor_data.get('bioguideId')
        
        # Parse introduced date
        introduced_date = None
        if bill.get('introducedDate'):
            try:
                from datetime import datetime
                introduced_date = datetime.fromisoformat(bill['introducedDate'].replace('Z', '+00:00'))
            except:
                introduced_date = None
        
        bill_data = {
            'congress': congress,
            'bill_number': bill_number,
            'bill_type': bill_type,
            'title': bill.get('title'),
            'short_title': bill.get('shortTitle'),
            'summary': bill.get('summary'),
            'introduced_date': introduced_date,
            'sponsor_bioguide_id': sponsor_id,
            'current_status': bill.get('latestAction', {}).get('actionBy'),
            'actions': actions,
            'subjects': subjects,
            'url': bill.get('url'),
            'api_url': bill.get('apiUrl')
        }
        
        return bill_data
    
    def get_representatives(self, congress: int, chamber: str = "house") -> List[Dict]:
        """Get representatives from a specific Congress and chamber.
        
        Args:
            congress: Congress number
            chamber: Chamber (house, senate)
            
        Returns:
            List of representative data dictionaries
        """
        # The Congress.gov API now returns all members, so we filter by chamber and congress
        endpoint = "/member"
        
        data = self._make_request(endpoint)
        if not data:
            return []
        
        representatives = []
        for member in data.get('members', []):
            # Check if this member has terms in the specified congress and chamber
            terms = member.get('terms', {}).get('item', [])
            has_valid_term = False
            
            for term in terms:
                term_chamber = term.get('chamber', '')
                start_year = term.get('startYear', 0)
                end_year = term.get('endYear', 9999)
                
                # Check if this term matches our criteria
                if ((chamber.lower() == 'house' and term_chamber == 'House of Representatives') or
                    (chamber.lower() == 'senate' and term_chamber == 'Senate')):
                    
                    # Check if this term overlaps with the congress
                    congress_start_year = 1789 + (congress - 1) * 2
                    congress_end_year = congress_start_year + 1
                    
                    # Be more flexible with year matching - include recent terms
                    if (start_year <= congress_end_year + 2 and 
                        (end_year >= congress_start_year - 2 or end_year == 0)):
                        has_valid_term = True
                        break
            
            if has_valid_term:
                # Parse the name into first and last
                full_name = member.get('name', '')
                name_parts = full_name.split(', ')
                if len(name_parts) >= 2:
                    last_name = name_parts[0]
                    first_name = name_parts[1]
                else:
                    first_name = full_name
                    last_name = ''
                
                rep_data = {
                    'bioguide_id': member.get('bioguideId'),
                    'congress_id': member.get('bioguideId'),  # Use bioguideId as congress_id for now
                    'full_name': full_name,
                    'first_name': first_name,
                    'last_name': last_name,
                    'state': member.get('state', ''),
                    'district': None,  # District info not available in this API response
                    'chamber': chamber,
                    'party': member.get('partyName', ''),
                    'start_date': datetime(2021, 1, 1),  # Default start date
                    'end_date': None,
                    'is_active': True
                }
                representatives.append(rep_data)
        
        return representatives
    
    def get_votes(self, congress: int, chamber: str, session: int = 1) -> List[Dict]:
        """Get voting records from a specific Congress, chamber, and session.
        
        Args:
            congress: Congress number
            chamber: Chamber (house, senate)
            session: Session number (1 or 2)
            
        Returns:
            List of vote data dictionaries
        """
        endpoint = f"/vote/{congress}/{chamber}/{session}"
        
        data = self._make_request(endpoint)
        if not data:
            return []
        
        votes = []
        for vote in data.get('votes', []):
            vote_data = {
                'congress': congress,
                'chamber': chamber,
                'session': session,
                'roll_call': vote.get('rollCall'),
                'vote_date': vote.get('date'),
                'question': vote.get('question'),
                'result': vote.get('result'),
                'bill': vote.get('bill'),
                'url': vote.get('url')
            }
            votes.append(vote_data)
        
        return votes
    
    def get_vote_details(self, congress: int, chamber: str, session: int, roll_call: int) -> Optional[Dict]:
        """Get detailed voting record for a specific roll call vote.
        
        Args:
            congress: Congress number
            chamber: Chamber
            session: Session number
            roll_call: Roll call number
            
        Returns:
            Detailed vote data or None
        """
        endpoint = f"/vote/{congress}/{chamber}/{session}/{roll_call}"
        
        data = self._make_request(endpoint)
        if not data:
            return None
        
        vote = data.get('vote', {})
        
        # Get individual vote positions
        positions = []
        for position in vote.get('positions', []):
            pos_data = {
                'member_id': position.get('memberId'),
                'name': position.get('name'),
                'vote_position': position.get('votePosition'),
                'state': position.get('state'),
                'district': position.get('district'),
                'party': position.get('party')
            }
            positions.append(pos_data)
        
        vote_data = {
            'congress': congress,
            'chamber': chamber,
            'session': session,
            'roll_call': roll_call,
            'vote_date': vote.get('date'),
            'question': vote.get('question'),
            'result': vote.get('result'),
            'bill': vote.get('bill'),
            'positions': positions,
            'url': vote.get('url')
        }
        
        return vote_data
    
    def search_bills(self, query: str, congress: Optional[int] = None, limit: int = 50) -> List[Dict]:
        """Search bills by text query.
        
        Args:
            query: Search query
            congress: Limit to specific Congress
            limit: Maximum results
            
        Returns:
            List of matching bills
        """
        endpoint = "/bill/search"
        params = {
            'query': query,
            'limit': limit
        }
        
        if congress:
            params['congress'] = congress
        
        data = self._make_request(endpoint, params)
        if not data:
            return []
        
        bills = []
        for bill in data.get('bills', []):
            bill_data = {
                'congress': bill.get('congress'),
                'bill_number': bill.get('number'),
                'bill_type': bill.get('billType'),
                'title': bill.get('title'),
                'summary': bill.get('summary'),
                'introduced_date': bill.get('introducedDate'),
                'url': bill.get('url')
            }
            bills.append(bill_data)
        
        return bills
    
    def get_committees(self, congress: int) -> List[Dict]:
        """Get committees for a specific Congress.
        
        Args:
            congress: Congress number
            
        Returns:
            List of committee data dictionaries
        """
        endpoint = f"/committee/{congress}"
        
        data = self._make_request(endpoint)
        if not data:
            return []
        
        committees = []
        for committee in data.get('committees', []):
            committee_data = {
                'congress_id': committee.get('id'),
                'name': committee.get('name'),
                'chamber': committee.get('chamber'),
                'committee_type': committee.get('type'),
                'parent_committee_id': committee.get('parentCommitteeId'),
                'url': committee.get('url')
            }
            committees.append(committee_data)
        
        return committees 