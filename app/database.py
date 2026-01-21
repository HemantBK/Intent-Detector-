import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.config import settings
from app.models import NormalizedListing, ConsumerIntent
import json


class DatabaseManager:
    def __init__(self):
        self.db = None
        self._initialize_firestore()
    
    def _initialize_firestore(self):
        """Initialize Firestore connection"""
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.firebase_credentials_path)
            firebase_admin.initialize_app(cred, {
                'projectId': settings.firebase_project_id,
            })
        self.db = firestore.client()
    
    def save_normalized_listing(self, listing: NormalizedListing) -> str:
        """Save normalized listing to Firestore"""
        doc_ref = self.db.collection('normalized_listings').document(listing.listing_id)
        doc_ref.set(json.loads(listing.model_dump_json()))
        return listing.listing_id
    
    def save_consumer_intent(self, intent: ConsumerIntent) -> str:
        """Save consumer intent to Firestore"""
        doc_ref = self.db.collection('consumer_intents').document(intent.intent_id)
        doc_ref.set(json.loads(intent.model_dump_json()))
        return intent.intent_id
    
    def query_intents(
        self,
        location: Optional[str] = None,
        intent_type: Optional[str] = None,
        min_confidence: float = 0.5,
        urgency: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query consumer intents with filters"""
        query = self.db.collection('consumer_intents')
        
        # Apply filters
        if location:
            query = query.where('city', '==', location.split(',')[0].strip())
        
        if intent_type:
            query = query.where('intent_type', '==', intent_type)
        
        if min_confidence:
            query = query.where('confidence_score', '>=', min_confidence)
        
        if urgency:
            query = query.where('urgency', '==', urgency)
        
        if start_date:
            query = query.where('detected_at', '>=', start_date)
        
        if end_date:
            query = query.where('detected_at', '<=', end_date)
        
        # Execute query
        query = query.limit(limit).order_by('detected_at', direction=firestore.Query.DESCENDING)
        results = query.stream()
        
        return [doc.to_dict() for doc in results]
    
    def get_intent_by_id(self, intent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific consumer intent by ID"""
        doc_ref = self.db.collection('consumer_intents').document(intent_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None


# Singleton instance
db_manager = DatabaseManager()
