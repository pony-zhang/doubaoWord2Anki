from typing import Dict, Any, List
from .config import settings
from loguru import logger

class DataTransformer:
    def __init__(self, field_mappings: Dict[str, str] = None):
        self.field_mappings = field_mappings or settings.field_mappings

    def transform_to_anki_notes(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform JSON data into Anki note format."""
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

    def _transform_single_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single data item into Anki note format."""
        note = {}
        for anki_field, source_field in self.field_mappings.items():
            note[anki_field] = item.get(source_field, "")