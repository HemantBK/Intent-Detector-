import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
import time
from app.models import RawListing, DataSource
from app.config import settings
from connectors.base_connector import BaseConnector
from utils.logger import logger


class CraigslistConnector(BaseConnector):
    """Connector for Craigslist car listings"""
    
    def __init__(self):
        super().__init__("craigslist.org")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def fetch_listings(
        self,
        location: str,
        radius_miles: int = 50,
        max_results: int = 50
    ) -> List[RawListing]:
        """Fetch car listings from Craigslist"""
        listings = []
        
        # Map location to Craigslist subdomain
        subdomain = self._get_subdomain(location)
        search_url = self._build_search_url(subdomain)
        
        logger.info(f"Fetching listings from Craigslist: {search_url}")
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            listing_items = soup.find_all('li', class_='result-row', limit=max_results)
            
            for item in listing_items:
                try:
                    raw_data = self.parse_listing(str(item))
                    
                    listing = RawListing(
                        source=DataSource.CRAIGSLIST,
                        url=raw_data.get('url', ''),
                        scraped_at=datetime.now(),
                        raw_html=str(item),
                        raw_data=raw_data
                    )
                    listings.append(listing)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse Craigslist listing: {e}")
                    continue
                
                time.sleep(settings.scraping_delay_seconds)
        
        except Exception as e:
            logger.error(f"Error fetching Craigslist listings: {e}")
        
        logger.info(f"Fetched {len(listings)} listings from Craigslist")
        return listings
    
    def parse_listing(self, raw_html: str) -> Dict[str, Any]:
        """Parse Craigslist listing item"""
        soup = BeautifulSoup(raw_html, 'lxml')
        data = {}
        
        # Title and URL
        title_elem = soup.find('a', class_='result-title')
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)
            data['url'] = title_elem.get('href', '')
        
        # Price
        price_elem = soup.find('span', class_='result-price')
        if price_elem:
            price_text = price_elem.get_text(strip=True).replace('$', '').replace(',', '')
            try:
                data['price'] = float(price_text)
            except:
                data['price'] = None
        
        # Location
        location_elem = soup.find('span', class_='result-hood')
        if location_elem:
            data['location'] = location_elem.get_text(strip=True).strip('()')
        
        # Date
        date_elem = soup.find('time', class_='result-date')
        if date_elem:
            data['listing_date'] = date_elem.get('datetime', '')
        
        return data
    
    def _build_search_url(self, subdomain: str) -> str:
        """Build Craigslist search URL"""
        return f"https://{subdomain}.craigslist.org/search/cta"
    
    def _get_subdomain(self, location: str) -> str:
        """Map location to Craigslist subdomain"""
        subdomain_mapping = {
            "Tucson, AZ": "tucson",
            "Phoenix, AZ": "phoenix",
            "Los Angeles, CA": "losangeles"
        }
        return subdomain_mapping.get(location, "tucson")
