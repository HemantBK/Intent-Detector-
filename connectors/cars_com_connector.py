import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
import time
import hashlib
from app.models import RawListing, DataSource
from app.config import settings
from connectors.base_connector import BaseConnector
from utils.logger import logger


class CarsComConnector(BaseConnector):
    """Connector for Cars.com listings"""
    
    BASE_URL = "https://www.cars.com"
    
    def __init__(self):
        super().__init__("cars.com")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def fetch_listings(
        self,
        location: str,
        radius_miles: int = 50,
        max_results: int = 50
    ) -> List[RawListing]:
        """Fetch car listings from Cars.com"""
        listings = []
        
        # Build search URL
        search_url = self._build_search_url(location, radius_miles)
        logger.info(f"Fetching listings from: {search_url}")
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            listing_cards = soup.find_all('div', class_='vehicle-card', limit=max_results)
            
            for card in listing_cards:
                try:
                    raw_data = self.parse_listing(str(card))
                    
                    listing = RawListing(
                        source=DataSource.CARS_COM,
                        url=raw_data.get('url', ''),
                        scraped_at=datetime.now(),
                        raw_html=str(card),
                        raw_data=raw_data
                    )
                    listings.append(listing)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse listing: {e}")
                    continue
                
                # Respectful delay
                time.sleep(settings.scraping_delay_seconds)
        
        except Exception as e:
            logger.error(f"Error fetching Cars.com listings: {e}")
        
        logger.info(f"Fetched {len(listings)} listings from Cars.com")
        return listings
    
    def parse_listing(self, raw_html: str) -> Dict[str, Any]:
        """Parse raw HTML card into structured data"""
        soup = BeautifulSoup(raw_html, 'lxml')
        
        data = {}
        
        # Title and URL
        title_elem = soup.find('h2', class_='title')
        if title_elem:
            link = title_elem.find('a')
            data['title'] = link.get_text(strip=True) if link else ''
            data['url'] = self.BASE_URL + link.get('href', '') if link else ''
        
        # Price
        price_elem = soup.find('span', class_='primary-price')
        if price_elem:
            price_text = price_elem.get_text(strip=True).replace('$', '').replace(',', '')
            try:
                data['price'] = float(price_text)
            except:
                data['price'] = None
        
        # Mileage
        mileage_elem = soup.find('div', class_='mileage')
        if mileage_elem:
            mileage_text = mileage_elem.get_text(strip=True).replace(',', '').replace(' mi.', '')
            try:
                data['mileage'] = int(mileage_text)
            except:
                data['mileage'] = None
        
        # Location
        location_elem = soup.find('div', class_='miles-from')
        if location_elem:
            data['location'] = location_elem.get_text(strip=True)
        
        # Dealer/Seller info
        dealer_elem = soup.find('div', class_='dealer-name')
        if dealer_elem:
            data['seller_name'] = dealer_elem.get_text(strip=True)
            data['seller_type'] = 'dealer'
        
        # Images
        img_elem = soup.find('img', class_='vehicle-image')
        if img_elem:
            data['images'] = [img_elem.get('src', '')]
        
        return data
    
    def _build_search_url(self, location: str, radius_miles: int = 50) -> str:
        """Build Cars.com search URL"""
        # Clean location (e.g., "Tucson, AZ" -> "tucson-az")
        location_slug = location.lower().replace(', ', '-').replace(' ', '-')
        return f"{self.BASE_URL}/shopping/results/?stock_type=all&makes[]=&models[]=&list_price_max=&maximum_distance={radius_miles}&zip={location_slug}"
