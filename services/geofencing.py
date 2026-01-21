from typing import Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from utils.logger import logger


class GeofencingService:
    """Handle location-based filtering"""
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent="consumer_intent_detector")
    
    def geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """Convert address to coordinates"""
        try:
            result = self.geocoder.geocode(location)
            if result:
                return (result.latitude, result.longitude)
        except Exception as e:
            logger.warning(f"Geocoding failed for '{location}': {e}")
        return None
    
    def is_within_radius(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float],
        radius_miles: float
    ) -> bool:
        """Check if two points are within radius"""
        try:
            distance = geodesic(point1, point2).miles
            return distance <= radius_miles
        except Exception as e:
            logger.error(f"Distance calculation failed: {e}")
            return False
    
    def filter_by_location(
        self,
        listings,
        target_location: str,
        radius_miles: float
    ):
        """Filter listings by geographic radius"""
        target_coords = self.geocode_location(target_location)
        if not target_coords:
            logger.warning(f"Could not geocode target location: {target_location}")
            return listings
        
        filtered = []
        for listing in listings:
            if listing.latitude and listing.longitude:
                listing_coords = (listing.latitude, listing.longitude)
                if self.is_within_radius(target_coords, listing_coords, radius_miles):
                    filtered.append(listing)
        
        return filtered


geofencing_service = GeofencingService()
