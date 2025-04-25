from pydantic import BaseSettings
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    # API settings
    api_endpoint: str = "https://www.doubao.com/samantha/word_notes/get"
    doubao_cookie: str = ""
    
    # Language settings
    language: str = "zh"
    source_lang: str = "en"
    target_lang: str = "zh"
    
    # HTTP Client settings
    request_timeout: int = 30
    max_retries: int = 3
    
    # Anki settings
    anki_connect_url: str = "http://localhost:8765"
    field_mappings: Dict[str, str] = {}
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()