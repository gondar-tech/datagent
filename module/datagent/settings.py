from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

class Settings(BaseModel):
    # App
    APP_NAME: str = "Avaloka Datagent"
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

def load_settings() -> Settings:
    return Settings(
        APP_NAME=os.getenv("APP_NAME", "Avaloka Datagent"),
        ENV=os.getenv("ENV", "development"),
        DEBUG=os.getenv("DEBUG", "true").lower() == "true",
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
        GROQ_API_KEY=os.getenv("GROQ_API_KEY"),
        DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///datagent.db"),
        RAY_ADDRESS=os.getenv("RAY_ADDRESS"),
        GITHUB_TOKEN=os.getenv("GITHUB_TOKEN"),
    )

settings = load_settings()
