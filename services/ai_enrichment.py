import openai
from typing import Dict, Any
import json
from app.models import NormalizedListing, ConsumerIntent, IntentType, IntentUrgency
from app.config import settings
from datetime import datetime
import hashlib
from utils.logger import logger

openai.api_key = settings.openai_api_key


class AIEnrichmentService:
    """Use OpenAI to detect consumer intent from listings"""
    
    SYSTEM_PROMPT = """You are an expert at detecting consumer purchase intent from marketplace listings.
    
Analyze the provided car listing and extract:
1. **Urgency**: How quickly the consumer wants to buy (high/medium/low)
2. **Confidence Score**: Likelihood this represents genuine buyer intent (0.0-1.0)
3. **Purchase Timeline**: Estimated timeframe (e.g., "within 1 week", "1-2 months")
4. **Budget Range**: Inferred price range the buyer is targeting
5. **Keywords**: Key search terms or preferences
6. **Preferences**: Any specific requirements (e.g., fuel type, features)

Consider factors like:
- Listing freshness (newer = higher urgency)
- Price positioning (deals = higher urgency)
- Description urgency signals ("must sell", "motivated seller")
- Contact availability (phone/email = higher intent)

Return ONLY valid JSON with this structure:
{
    "urgency": "high|medium|low",
    "confidence_score": 0.85,
    "purchase_timeline": "within 1 week",
    "budget_min": 15000,
    "budget_max": 25000,
    "keywords": ["SUV", "low mileage", "4WD"],
    "preferences": {
        "vehicle_type": "SUV",
        "max_mileage": 50000,
        "features": ["4WD", "leather seats"]
    }
}
"""
    
    @staticmethod
    async def enrich_listing(normalized_listing: NormalizedListing) -> ConsumerIntent:
        """Use LLM to extract consumer intent signals"""
        
        # Build context for LLM
        listing_context = AIEnrichmentService._build_listing_context(normalized_listing)
        
        try:
            # Call OpenAI API
            response = openai.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": AIEnrichmentService.SYSTEM_PROMPT},
                    {"role": "user", "content": listing_context}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse response
            ai_output = json.loads(response.choices[0].message.content)
            
            # Build ConsumerIntent object
            intent = ConsumerIntent(
                intent_id=AIEnrichmentService._generate_intent_id(normalized_listing),
                intent_type=IntentType.CAR_BUYER,
                location=normalized_listing.location,
                city=normalized_listing.city or "Unknown",
                state=normalized_listing.state or "Unknown",
                latitude=normalized_listing.latitude,
                longitude=normalized_listing.longitude,
                urgency=IntentUrgency(ai_output.get('urgency', 'medium')),
                confidence_score=ai_output.get('confidence_score', 0.5),
                purchase_timeline=ai_output.get('purchase_timeline'),
                budget_min=ai_output.get('budget_min'),
                budget_max=ai_output.get('budget_max'),
                keywords=ai_output.get('keywords', []),
                preferences=ai_output.get('preferences', {}),
                source_listing=normalized_listing,
                detected_at=datetime.now(),
                contact_available=bool(normalized_listing.phone or normalized_listing.email),
                contact_info={
                    'phone': normalized_listing.phone,
                    'email': normalized_listing.email,
                    'seller_name': normalized_listing.seller_name
                } if (normalized_listing.phone or normalized_listing.email) else None
            )
            
            logger.info(f"✅ AI enrichment complete: {intent.intent_id} (confidence: {intent.confidence_score})")
            return intent
            
        except Exception as e:
            logger.error(f"❌ AI enrichment failed: {e}")
            raise
    
    @staticmethod
    def _build_listing_context(listing: NormalizedListing) -> str:
        """Build context string for LLM"""
        context = f"""
**Car Listing Analysis**

Title: {listing.title}
Price: ${listing.price:,.0f if listing.price else 'Not listed'}
Mileage: {listing.mileage:,} miles
Location: {listing.location}
Seller: {listing.seller_name or 'Unknown'} ({listing.seller_type})
Source: {listing.source}
Listed: {listing.listing_date.strftime('%Y-%m-%d') if listing.listing_date else 'Unknown'}
Scraped: {listing.scraped_at.strftime('%Y-%m-%d')}

Description: {listing.description[:500] if listing.description else 'No description available'}

Contact Available: {'Yes' if (listing.phone or listing.email) else 'No'}
"""
        return context.strip()
    
    @staticmethod
    def _generate_intent_id(listing: NormalizedListing) -> str:
        """Generate unique intent ID"""
        unique_string = f"intent_{listing.listing_id}_{datetime.now().isoformat()}"
        return hashlib.md5(unique_string.encode()).hexdigest()
