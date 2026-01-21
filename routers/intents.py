from fastapi import APIRouter, HTTPException, Query
from app.models import IntentQueryRequest, IntentType, IntentUrgency
from app.database import db_manager
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.logger import logger

router = APIRouter()


@router.post("/query", response_model=Dict[str, Any])
async def query_intents(request: IntentQueryRequest):
    """
    Query consumer intents with filters
    
    - **location**: Filter by city/location
    - **intent_type**: Type of consumer intent
    - **min_confidence**: Minimum confidence score (0.0-1.0)
    - **urgency**: Filter by urgency level
    - **start_date**: Filter intents after this date
    - **end_date**: Filter intents before this date
    - **limit**: Maximum results to return
    """
    try:
        results = db_manager.query_intents(
            location=request.location,
            intent_type=request.intent_type.value if request.intent_type else None,
            min_confidence=request.min_confidence,
            urgency=request.urgency.value if request.urgency else None,
            start_date=request.start_date,
            end_date=request.end_date,
            limit=request.limit
        )
        
        logger.info(f"📊 Query returned {len(results)} consumer intents")
        
        return {
            "total_results": len(results),
            "filters_applied": {
                "location": request.location,
                "intent_type": request.intent_type,
                "min_confidence": request.min_confidence,
                "urgency": request.urgency
            },
            "intents": results
        }
    
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{intent_id}", response_model=Dict[str, Any])
async def get_intent_by_id(intent_id: str):
    """Retrieve a specific consumer intent by ID"""
    intent = db_manager.get_intent_by_id(intent_id)
    
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    return intent


@router.get("/stats/summary")
async def get_stats_summary():
    """Get summary statistics of detected intents"""
    # In production, implement aggregation queries
    return {
        "message": "Stats coming soon",
        "total_intents": 0,
        "high_urgency_count": 0,
        "avg_confidence": 0.0
    }
