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
    mastered: Optional[bool] = False
    sentences: Optional[List[str]] = None

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON format"""
        return {
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "word": self.word,
            "translate": self.translate
        }

    def to_csv_row(self) -> Dict[str, str]:
        """Convert to CSV row format"""
        return {
            "word": self.word,
            "translation": self.translate,
            "phonetic": self.phonetic or "",
            "mastered": "Yes" if self.mastered else "No",
            "sentences": "\n".join(self.sentences) if self.sentences else ""
        }

    @classmethod
    def from_csv_row(cls, row: Dict[str, str], source_lang: str = "en", target_lang: str = "zh") -> "WordNote":
        """Create WordNote from CSV row"""
        sentences = row.get("sentences", "").split("\n") if row.get("sentences") else []
        return cls(
            source_lang=source_lang,
            target_lang=target_lang,
            word=row["word"],
            translate=row["translation"],
            phonetic=row.get("phonetic", ""),
            mastered=row.get("mastered", "").lower() == "yes",
            sentences=[s for s in sentences if s.strip()]
        )

class WordNotesResponse(BaseModel):
    """Response data containing word notes"""
    word_notes: List[WordNote]

class ApiResponse(BaseModel):
    """API response model"""
    code: int
    msg: str
    data: Optional[Dict[str, Any]]