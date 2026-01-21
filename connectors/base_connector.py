from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.models import RawListing


class BaseConnector(ABC):
    """Base class for all data source connectors"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
    
    @abstractmethod
    async def fetch_listings(
        self,
        location: str,
        radius_miles: int,
        max_results: int
    ) -> List[RawListing]:
        """Fetch listings from the data source"""
        pass
    
    @abstractmethod
    def parse_listing(self, raw_html: str) -> Dict[str, Any]:
        """Parse raw HTML into structured data"""
        pass
    
    def _build_search_url(self, location: str, **kwargs) -> str:
        """Build search URL for the data source"""
        raise NotImplementedError
