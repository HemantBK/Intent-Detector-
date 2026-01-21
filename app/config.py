from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    
    # Firebase Configuration
    firebase_project_id: Optional[str] = None
    firebase_credentials_path: str = "./firebase-credentials.json"
    
    # Application Settings
    environment: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Data Collection Settings
    default_location: str = "Tucson, AZ"
    default_radius_miles: int = 50
    scraping_delay_seconds: int = 2
    
    # Rate Limiting
    max_requests_per_minute: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
