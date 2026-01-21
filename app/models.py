from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class IntentType(str, Enum):
    CAR_BUYER = "car_buyer"
    HOME_BUYER = "home_buyer"
    RENTAL_SEEKER = "rental_seeker"
    SERVICE_SEEKER = "service_seeker"


class IntentUrgency(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DataSource(str, Enum):
    CARS_COM = "cars.com"
    AUTOTRADER = "autotrader.com"
    CRAIGSLIST = "craigslist.org"


class RawListing(BaseModel):
    source: DataSource
    url: str
    scraped_at: datetime
    raw_html: Optional[str] = None
    raw_data: Dict[str, Any]


class NormalizedListing(BaseModel):
    listing_id: str
    source: DataSource
    url: str
    
    # Vehicle Details
    title: str
    price: Optional[float] = None
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    mileage: Optional[int] = None
    condition: Optional[str] = None
    
    # Location
    location: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Contact Info
    seller_name: Optional[str] = None
    seller_type: Optional[str] = None  # dealer, private
    phone: Optional[str] = None
    email: Optional[str] = None
    
    # Metadata
    description: Optional[str] = None
    images: List[str] = []
    listing_date: Optional[datetime] = None
    scraped_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConsumerIntent(BaseModel):
    intent_id: str
    intent_type: IntentType
    
    # Consumer Information
    location: str
    city: str
    state: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Intent Details
    urgency: IntentUrgency
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    purchase_timeline: Optional[str] = None  # "within 1 week", "1-2 months"
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    
    # AI-Extracted Entities
    keywords: List[str] = []
    preferences: Dict[str, Any] = {}
    
    # Source Data
    source_listing: NormalizedListing
    detected_at: datetime
    
    # Contact Information (if available)
    contact_available: bool = False
    contact_info: Optional[Dict[str, str]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class IntentQueryRequest(BaseModel):
    location: Optional[str] = None
    intent_type: Optional[IntentType] = None
    min_confidence: float = Field(0.5, ge=0.0, le=1.0)
    urgency: Optional[IntentUrgency] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)


class IngestionRequest(BaseModel):
    location: str = "Tucson, AZ"
    radius_miles: int = 50
    sources: List[DataSource] = [DataSource.CARS_COM]
    max_listings: int = 50
