from typing import Dict, Any, List
from .config import settings, WordNote
from loguru import logger

class DataTransformer:
    def __init__(self, field_mappings: Dict[str, str] = None):
        """Initialize transformer with field mappings
        
        If no mappings provided, uses default mapping:
        - Front: word
        - Back: translate
        """
        if not field_mappings:
            self.field_mappings = {
                "Front": "word",
                "Back": "translate"
            }
        else:
            self.field_mappings = field_mappings

    def transform_to_anki_notes(self, data: List[WordNote]) -> List[Dict[str, str]]:
        """Transform word notes into Anki note format."""
        anki_notes = []
        for item in data:
            try:
                note = self._transform_single_item(item)
                if note:
                    anki_notes.append(note)
            except Exception as e:
                logger.error(f"Error transforming item {item}: {e}")
                continue
        return anki_notes

    def _transform_single_item(self, item: WordNote) -> Dict[str, str]:
        """Transform a single word note into Anki note format."""
        note = {}
        item_dict = item.model_dump()  # Convert Pydantic model to dict
        
        for anki_field, source_field in self.field_mappings.items():
            note[anki_field] = item_dict.get(source_field, "")
        
        return note