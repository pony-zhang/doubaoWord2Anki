from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class WordNote(BaseModel):
    """Word note data model"""
    source_lang: str
    target_lang: str
    word: str
    translate: str
    phonetic: Optional[str] = None
    examples: Optional[List[str]] = None
    collins: Optional[Dict[str, Any]] = None
    additional_info: Optional[Dict[str, Any]] = None

class WordNotesResponse(BaseModel):
    """Response data containing word notes"""
    word_notes: List[WordNote]

class ApiResponse(BaseModel):
    """API response model"""
    code: int
    msg: str
    data: Optional[Dict[str, Any]]