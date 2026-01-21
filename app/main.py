from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import ingestion, intents
from utils.logger import logger
import uvicorn


app = FastAPI(
    title="Consumer Intent Detector API",
    description="Domain-agnostic consumer intent detection from public data sources",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingestion.router, prefix="/api/v1/ingestion", tags=["Ingestion"])
app.include_router(intents.router, prefix="/api/v1/intents", tags=["Intents"])


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Consumer Intent Detector API starting up...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Default Location: {settings.default_location}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Shutting down Consumer Intent Detector API...")


@app.get("/")
async def root():
    return {
        "message": "Consumer Intent Detector API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2026-01-21T22:00:00Z"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )
