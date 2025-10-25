"""
GovInfo API integration for AyeSpy.
Provides access to congressional transcripts and documents.
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import time
import json
from bs4 import BeautifulSoup

load_dotenv()

logger = logging.getLogger(__name__)


class GovInfoAPI:
    """GovInfo API client for retrieving congressional documents and transcripts."""
    
    BASE_URL = "https://api.govinfo.gov"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize GovInfo API client.
        
        Args:
            api_key: GovInfo API key. If None, uses environment variable.
        """
        self.api_key = api_key or os.getenv('GOVINFO_API_KEY')
        if not self.api_key:
            logger.warning("No GovInfo API key provided. Some endpoints may not work.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AyeSpy/1.0 (Congressional Transparency Platform)',
            'Accept': 'application/json'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 200ms between requests
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a rate-limited request to the GovInfo API.
        
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
    
    def get_congressional_hearings(self, congress: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get congressional hearings from a specific Congress.
        
        Args:
            congress: Congress number
            limit: Maximum number of hearings to return
            offset: Offset for pagination
            
        Returns:
            List of hearing data dictionaries
        """
        endpoint = "/collections/CHRG"
        params = {
            'congress': congress,
            'limit': limit,
            'offset': offset,
            'pageSize': limit
        }
        
        data = self._make_request(endpoint, params)
        if not data:
            return []
        
        hearings = []
        for package in data.get('packages', []):
            hearing_data = {
                'congress': congress,
                'package_id': package.get('packageId'),
                'title': package.get('title'),
                'date_issued': package.get('dateIssued'),
                'last_modified': package.get('lastModified'),
                'package_link': package.get('packageLink'),
                'pdf_link': package.get('pdfLink'),
                'htm_link': package.get('htmLink'),
                'xml_link': package.get('xmlLink'),
                'granule_class': package.get('granuleClass'),
                'collection_code': package.get('collectionCode')
            }
            hearings.append(hearing_data)
        
        return hearings
    
    def get_hearing_transcript(self, package_id: str) -> Optional[Dict]:
        """Get the transcript content for a specific hearing.
        
        Args:
            package_id: GovInfo package ID
            
        Returns:
            Transcript data or None
        """
        endpoint = f"/packages/{package_id}/htm"
        
        data = self._make_request(endpoint)
        if not data:
            return None
        
        # Parse HTML content to extract transcript
        html_content = data.get('content', '')
        if not html_content:
            return None
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text() if title else "Unknown Title"
            
            # Extract transcript text
            transcript_text = ""
            
            # Look for common transcript patterns
            # This will need to be refined based on actual GovInfo HTML structure
            content_divs = soup.find_all(['div', 'p', 'span'])
            for div in content_divs:
                text = div.get_text(strip=True)
                if text and len(text) > 20:  # Filter out short text
                    transcript_text += text + "\n"
            
            transcript_data = {
                'package_id': package_id,
                'title': title_text,
                'transcript_text': transcript_text,
                'html_content': html_content,
                'extracted_at': datetime.now().isoformat()
            }
            
            return transcript_data
            
        except Exception as e:
            logger.error(f"Failed to parse transcript HTML: {e}")
            return None
    
    def search_hearings(self, query: str, congress: Optional[int] = None, 
                        start_date: Optional[str] = None, end_date: Optional[str] = None,
                        limit: int = 50) -> List[Dict]:
        """Search congressional hearings by text query.
        
        Args:
            query: Search query
            congress: Limit to specific Congress
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum results
            
        Returns:
            List of matching hearings
        """
        endpoint = "/search"
        params = {
            'query': query,
            'collection': 'CHRG',
            'limit': limit
        }
        
        if congress:
            params['congress'] = congress
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        
        data = self._make_request(endpoint, params)
        if not data:
            return []
        
        hearings = []
        for result in data.get('results', []):
            hearing_data = {
                'package_id': result.get('packageId'),
                'title': result.get('title'),
                'date_issued': result.get('dateIssued'),
                'congress': result.get('congress'),
                'collection_code': result.get('collectionCode'),
                'package_link': result.get('packageLink'),
                'score': result.get('score')
            }
            hearings.append(hearing_data)
        
        return hearings
    
    def get_recent_hearings(self, days: int = 30, limit: int = 100) -> List[Dict]:
        """Get recent congressional hearings from the last N days.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of hearings to return
            
        Returns:
            List of recent hearings
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return self.search_hearings(
            query="congressional hearing",
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            limit=limit
        )
    
    def get_hearing_metadata(self, package_id: str) -> Optional[Dict]:
        """Get metadata for a specific hearing package.
        
        Args:
            package_id: GovInfo package ID
            
        Returns:
            Hearing metadata or None
        """
        endpoint = f"/packages/{package_id}/summary"
        
        data = self._make_request(endpoint)
        if not data:
            return None
        
        package = data.get('package', {})
        
        metadata = {
            'package_id': package_id,
            'title': package.get('title'),
            'date_issued': package.get('dateIssued'),
            'last_modified': package.get('lastModified'),
            'collection_code': package.get('collectionCode'),
            'granule_class': package.get('granuleClass'),
            'congress': package.get('congress'),
            'session': package.get('session'),
            'chamber': package.get('chamber'),
            'committee': package.get('committee'),
            'bill_numbers': package.get('billNumbers'),
            'subjects': package.get('subjects'),
            'package_link': package.get('packageLink'),
            'pdf_link': package.get('pdfLink'),
            'htm_link': package.get('htmLink'),
            'xml_link': package.get('xmlLink')
        }
        
        return metadata
    
    def get_collection_summary(self, collection: str = "CHRG") -> Optional[Dict]:
        """Get summary information about a collection.
        
        Args:
            collection: Collection code (CHRG for hearings)
            
        Returns:
            Collection summary or None
        """
        endpoint = f"/collections/{collection}/summary"
        
        data = self._make_request(endpoint)
        if not data:
            return None
        
        return data.get('collection', {})
    
    def get_package_download_urls(self, package_id: str) -> Optional[Dict]:
        """Get download URLs for different formats of a package.
        
        Args:
            package_id: GovInfo package ID
            
        Returns:
            Dictionary of format URLs or None
        """
        endpoint = f"/packages/{package_id}/download"
        
        data = self._make_request(endpoint)
        if not data:
            return None
        
        downloads = data.get('download', {})
        
        return {
            'pdf': downloads.get('pdf'),
            'htm': downloads.get('htm'),
            'xml': downloads.get('xml'),
            'txt': downloads.get('txt')
        }
    
    def get_hearing_by_date_range(self, start_date: str, end_date: str, 
                                 congress: Optional[int] = None, limit: int = 100) -> List[Dict]:
        """Get hearings within a specific date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            congress: Limit to specific Congress
            limit: Maximum results
            
        Returns:
            List of hearings in date range
        """
        return self.search_hearings(
            query="congressional hearing",
            congress=congress,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        ) 