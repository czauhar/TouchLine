from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./touchline.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Twilio SMS
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Sports API
    API_FOOTBALL_KEY: Optional[str] = None
    SPORTS_API_BASE_URL: str = "https://v3.football.api-sports.io/"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Monitoring
    MONITORING_INTERVAL: int = 60  # seconds
    MAX_RETRIES: int = 3
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,https://touchline.app,https://www.touchline.app"
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )

settings = Settings() 