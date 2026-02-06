from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # App
    ENV: str = "development"
    DEBUG: bool = True

    # LLM
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///datagent.db"
    
    # Ray
    RAY_ADDRESS: Optional[str] = None
    
    # Github
    GITHUB_TOKEN: Optional[str] = None
    
    # Storage
    STORAGE_ROOT: str = "module/datagent/db/storage"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
