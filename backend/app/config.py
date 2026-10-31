import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Inventory & Supply Chain Demand Planning System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database URL: default to SQLite for standalone ease, or PostgreSQL when configured
    # e.g., postgresql+psycopg2://postgres:postgres@localhost:5432/supply_chain
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./supply_chain.db"
    )
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    RANDOM_SEED: int = 20261022
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
