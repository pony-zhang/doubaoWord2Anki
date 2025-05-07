from typing import Dict, Any, List
from ..core.interfaces import DataMiddleware
from ..core.models import WordNote
import logging

logger = logging.getLogger(__name__)


class FieldMappingMiddleware(DataMiddleware):
    """Middleware for mapping word note fields to Anki note fields"""
    
    def __init__(self, field_mappings: Dict[str, str] = None):
        """Initialize field mapping middleware
        
        Args:
            field_mappings: Dictionary mapping Anki fields to WordNote attributes
        """
        if not field_mappings:
            self.field_mappings = {
                "Front": "word",
                "Back": "translate",
                "Phonetic": "phonetic",
                "Examples": "examples",
                "Collins": "collins"
            }
        else:
            self.field_mappings = field_mappings

    async def process(self, data: List[WordNote]) -> List[Dict[str, Any]]:
        """Transform word notes into Anki note format
        
        Args:
            data: List of word notes to transform
            
        Returns:
            List of dictionaries with Anki field mappings
        """
        anki_notes = []
        
        for note in data:
            try:
                anki_note = self._map_fields(note)
                anki_notes.append(anki_note)
            except Exception as e:
                logger.error(f"Error mapping fields for word {note.word}: {e}")
                continue
                
        return anki_notes

    def _map_fields(self, note: WordNote) -> Dict[str, str]:
        """Map a single word note to Anki fields
        
        Args:
            note: Word note to transform
            
        Returns:
            Dictionary with Anki field mappings
        """
        anki_note = {}
        
        for anki_field, note_field in self.field_mappings.items():
            try:
                value = getattr(note, note_field, None)
                
                if value is not None:
                    if isinstance(value, list):
                        # Format example sentences
                        if note_field == "examples":
                            value = self._format_examples(value)
                    elif isinstance(value, dict):
                        # Format Collins data
                        if note_field == "collins":
                            value = self._format_collins_data(value)
                            
                    anki_note[anki_field] = str(value)
                    
            except Exception as e:
                logger.warning(f"Error mapping field {note_field}: {e}")
                continue
                
        return anki_note

    def _format_examples(self, examples: List[str], max_examples: int = 3) -> str:
        """Format example sentences nicely"""
        if not examples:
            return ""
        formatted = []
        for i, example in enumerate(examples[:max_examples], 1):
            formatted.append(f"{i}. {example}")
        return "\n".join(formatted)

    def _format_collins_data(self, collins: Dict[str, Any]) -> str:
        """Format Collins dictionary data nicely"""
        formatted = []
        
        if 'translations' in collins:
            formatted.extend(collins['translations'])
            
        if 'examples' in collins:
            examples = [f"• {ex['en']}\n  {ex['zh']}" 
                       for ex in collins['examples'][:2]]
            formatted.extend(examples)
            
        return "\n\n".join(formatted)