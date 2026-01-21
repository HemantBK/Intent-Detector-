from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models import IngestionRequest, DataSource
from connectors.cars_com_connector import CarsComConnector
from connectors.autotrader_connector import AutoTraderConnector
from connectors.craigslist_connector import CraigslistConnector
from services.normalizer import DataNormalizer
from services.ai_enrichment import AIEnrichmentService
from app.database import db_manager
from utils.logger import logger
from typing import Dict, Any

router = APIRouter()

# Initialize connectors
connectors = {
    DataSource.CARS_COM: CarsComConnector(),
    DataSource.AUTOTRADER: AutoTraderConnector(),
    DataSource.CRAIGSLIST: CraigslistConnector()
}


async def process_ingestion(request: IngestionRequest):
    """Background task to process data ingestion"""
    total_intents = 0
    
    for source in request.sources:
        connector = connectors.get(source)
        if not connector:
            logger.warning(f"No connector for source: {source}")
            continue
        
        try:
            # Step 1: Fetch raw listings
            logger.info(f"📥 Fetching listings from {source}...")
            raw_listings = await connector.fetch_listings(
                location=request.location,
                radius_miles=request.radius_miles,
                max_results=request.max_listings
            )
            
            # Step 2: Normalize data
            logger.info(f"🔄 Normalizing {len(raw_listings)} listings...")
            for raw_listing in raw_listings:
                try:
                    normalized = DataNormalizer.normalize_listing(raw_listing)
                    db_manager.save_normalized_listing(normalized)
                    
                    # Step 3: AI enrichment
                    logger.info(f"🤖 Enriching with AI: {normalized.listing_id}...")
                    intent = await AIEnrichmentService.enrich_listing(normalized)
                    db_manager.save_consumer_intent(intent)
                    
                    total_intents += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process listing: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error processing source {source}: {e}")
    
    logger.info(f"✅ Ingestion complete: {total_intents} consumer intents detected")


@router.post("/start", response_model=Dict[str, Any])
async def start_ingestion(
    request: IngestionRequest,
    background_tasks: BackgroundTasks
):
    """
    Start data ingestion from specified sources
    
    - **location**: Target location (e.g., "Tucson, AZ")
    - **radius_miles**: Search radius in miles
    - **sources**: List of data sources to scrape
    - **max_listings**: Maximum listings per source
    """
    logger.info(f"🚀 Starting ingestion for {request.location}")
    
    # Add to background tasks
    background_tasks.add_task(process_ingestion, request)
    
    return {
        "status": "started",
        "message": f"Data ingestion initiated for {request.location}",
        "location": request.location,
        "sources": [s.value for s in request.sources],
        "max_listings": request.max_listings
    }


@router.get("/status")
async def get_ingestion_status():
    """Get current ingestion status"""
    # In production, track via Redis or database
    return {
        "status": "operational",
        "message": "Use POST /start to begin data collection"
    }
