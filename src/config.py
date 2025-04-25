from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class WordNote(BaseModel):
    """Word note data model"""
    source_lang: str
    target_lang: str
    word: str
    translate: str

class WordNotesResponse(BaseModel):
    """API response data model"""
    word_notes: List[WordNote]

class ApiResponse(BaseModel):
    """API response wrapper"""
    code: int
    msg: str
    data: Optional[Dict[str, Any]] = None  # Make data optional and allow any structure

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
    deck_name: str = "Doubao Words"
    model_name: str = "Basic"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()