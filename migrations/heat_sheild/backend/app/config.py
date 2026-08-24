"""
Backend application configuration and environment variables settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATA_MODE: str = "fixture"  # 'fixture' or 'live'
    FORTYGUARD_BASE_URL: str = "https://api.fortyguard.io/v1"
    FORTYGUARD_API_KEY: Optional[str] = None
    CENSUS_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
