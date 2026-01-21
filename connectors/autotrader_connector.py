import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
import time
from app.models import RawListing, DataSource
from app.config import settings
from connectors.base_connector import BaseConnector
from utils.logger import logger


class AutoTraderConnector(BaseConnector):
    """Connector for AutoTrader listings"""
    
    BASE_URL = "https://www.autotrader.com"
    
    def __init__(self):
        super().__init__("autotrader.com")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def fetch_listings(
        self,
        location: str,
        radius_miles: int = 50,
        max_results: int = 50
    ) -> List[RawListing]:
        """Fetch car listings from AutoTrader"""
        listings = []
        
        # Extract ZIP from location (simplified - you'd want geocoding here)
        zip_code = self._extract_zip(location)
        search_url = self._build_search_url(zip_code, radius_miles)
        
        logger.info(f"Fetching listings from AutoTrader: {search_url}")
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            listing_cards = soup.find_all('div', attrs={'data-cmp': 'inventoryListing'}, limit=max_results)
            
            for card in listing_cards:
                try:
                    raw_data = self.parse_listing(str(card))
                    
                    listing = RawListing(
                        source=DataSource.AUTOTRADER,
                        url=raw_data.get('url', ''),
                        scraped_at=datetime.now(),
                        raw_html=str(card),
                        raw_data=raw_data
                    )
                    listings.append(listing)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse AutoTrader listing: {e}")
                    continue
                
                time.sleep(settings.scraping_delay_seconds)
        
        except Exception as e:
            logger.error(f"Error fetching AutoTrader listings: {e}")
        
        logger.info(f"Fetched {len(listings)} listings from AutoTrader")
        return listings
    
    def parse_listing(self, raw_html: str) -> Dict[str, Any]:
        """Parse AutoTrader listing card"""
        soup = BeautifulSoup(raw_html, 'lxml')
        data = {}
        
        # Title
        title_elem = soup.find('div', class_='item-title')
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)
        
        # Price
        price_elem = soup.find('span', class_='item-price')
        if price_elem:
            price_text = price_elem.get_text(strip=True).replace('$', '').replace(',', '')
            try:
                data['price'] = float(price_text)
            except:
                data['price'] = None
        
        # Mileage
        mileage_elem = soup.find('span', class_='item-mileage')
        if mileage_elem:
            mileage_text = mileage_elem.get_text(strip=True).replace(',', '').replace(' mi', '')
            try:
                data['mileage'] = int(mileage_text)
            except:
                data['mileage'] = None
        
        # Location
        location_elem = soup.find('span', class_='item-location')
        if location_elem:
            data['location'] = location_elem.get_text(strip=True)
        
        return data
    
    def _build_search_url(self, zip_code: str, radius_miles: int) -> str:
        """Build AutoTrader search URL"""
        return f"{self.BASE_URL}/cars-for-sale/all-cars/{zip_code}?searchRadius={radius_miles}"
    
    def _extract_zip(self, location: str) -> str:
        """Extract or default ZIP code from location string"""
        # Simplified - would use geocoding in production
        zip_mapping = {
            "Tucson, AZ": "85701",
            "Phoenix, AZ": "85001",
            "Los Angeles, CA": "90001"
        }
        return zip_mapping.get(location, "85701")
