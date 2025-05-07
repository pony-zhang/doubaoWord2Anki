import os
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
from dotenv import load_dotenv

load_dotenv()

class WordNote(BaseModel):
    """Word note data model"""
    source_lang: str
    target_lang: str
    word: str
    translate: str

class WordNotesResponse(BaseModel):
    """Response data containing word notes"""
    word_notes: List[WordNote]

class ApiResponse(BaseModel):
    """API response model"""
    code: int
    msg: str
    data: Optional[Dict[str, Any]]

class DictionaryConfig(BaseModel):
    """Dictionary service configuration"""
    endpoint: str
    user_agent: Optional[str] = None
    keyfrom: Optional[str] = None

class DictionariesConfig(BaseModel):
    """All dictionary services configuration"""
    youdao: DictionaryConfig
    collins: DictionaryConfig
    renren: DictionaryConfig

class DouBaoConfig(BaseModel):
    """DouBao API configuration"""
    endpoint: str
    cookie: str

class ApiConfig(BaseModel):
    """API configuration"""
    doubao: DouBaoConfig
    dictionaries: DictionariesConfig

class LanguageConfig(BaseModel):
    """Language settings"""
    default: str = "zh"
    source: str = "en"
    target: str = "zh"

class HttpHeadersConfig(BaseModel):
    """HTTP headers configuration"""
    user_agent: str
    accept: str = "application/json"
    content_type: str = "application/json"

class HttpConfig(BaseModel):
    """HTTP client settings"""
    timeout: int = 30
    max_retries: int = 3
    headers: HttpHeadersConfig

class AnkiConfig(BaseModel):
    """Anki settings"""
    connect_url: str = "http://localhost:8765"
    deck_name: str = "Doubao Vocabulary"
    model_name: str = "Basic"
    field_mappings: Dict[str, str]

class CacheConfig(BaseModel):
    """Cache settings"""
    enabled: bool = True
    file: str = "word_cache.json"
    directory: str = "~/.doubao"

class Config(BaseModel):
    """Main configuration"""
    api: ApiConfig
    language: LanguageConfig
    http: HttpConfig
    anki: AnkiConfig
    cache: CacheConfig

def load_config() -> Config:
    """Load configuration from YAML file"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    config_data['api']['doubao']['cookie'] = os.getenv("COOKIE")
    return Config(**config_data)

# Global configuration instance
settings = load_config()