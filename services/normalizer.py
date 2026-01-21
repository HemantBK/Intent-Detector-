from typing import Dict, Any
from datetime import datetime
import hashlib
from app.models import RawListing, NormalizedListing, DataSource
from utils.logger import logger


class DataNormalizer:
    """Normalize data from different sources into unified schema"""
    
    @staticmethod
    def normalize_listing(raw_listing: RawListing) -> NormalizedListing:
        """Convert raw listing to normalized format"""
        raw_data = raw_listing.raw_data
        
        # Generate unique listing ID
        listing_id = DataNormalizer._generate_listing_id(
            raw_listing.source,
            raw_data.get('url', ''),
            raw_data.get('title', '')
        )
        
        # Extract location components
        location = raw_data.get('location', '')
        city, state, zip_code = DataNormalizer._parse_location(location)
        
        # Build normalized listing
        normalized = NormalizedListing(
            listing_id=listing_id,
            source=raw_listing.source,
            url=raw_data.get('url', raw_listing.url),
            title=raw_data.get('title', 'Unknown'),
            price=raw_data.get('price'),
            year=raw_data.get('year'),
            make=raw_data.get('make'),
            model=raw_data.get('model'),
            mileage=raw_data.get('mileage'),
            condition=raw_data.get('condition'),
            location=location,
            city=city,
            state=state,
            zip_code=zip_code,
            latitude=raw_data.get('latitude'),
            longitude=raw_data.get('longitude'),
            seller_name=raw_data.get('seller_name'),
            seller_type=raw_data.get('seller_type', 'unknown'),
            phone=raw_data.get('phone'),
            email=raw_data.get('email'),
            description=raw_data.get('description'),
            images=raw_data.get('images', []),
            listing_date=DataNormalizer._parse_date(raw_data.get('listing_date')),
            scraped_at=raw_listing.scraped_at
        )
        
        logger.debug(f"Normalized listing: {listing_id}")
        return normalized
    
    @staticmethod
    def _generate_listing_id(source: DataSource, url: str, title: str) -> str:
        """Generate unique hash-based ID for listing"""
        unique_string = f"{source}_{url}_{title}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    @staticmethod
    def _parse_location(location_str: str) -> tuple:
        """Extract city, state, zip from location string"""
        if not location_str:
            return None, None, None
        
        parts = location_str.split(',')
        city = parts[0].strip() if len(parts) > 0 else None
        state = parts[1].strip() if len(parts) > 1 else None
        zip_code = parts[2].strip() if len(parts) > 2 else None
        
        return city, state, zip_code
    
    @staticmethod
    def _parse_date(date_str: Any) -> datetime:
        """Parse date string to datetime"""
        if isinstance(date_str, datetime):
            return date_str
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(str(date_str))
        except:
            return None
