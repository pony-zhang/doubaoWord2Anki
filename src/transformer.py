from typing import Dict, Any, List, Optional
from .config import settings, WordNote
from loguru import logger
from .services.dictionary_factory import DictionaryFactory
import asyncio

class DataTransformer:
    def __init__(
        self, 
        field_mappings: Dict[str, str] = None,
        dictionary_service: str = 'youdao',
        include_examples: bool = True,
        include_phonetic: bool = True,
        include_collins: bool = True
    ):
        """Initialize transformer with options
        
        Args:
            field_mappings: Custom field mappings for Anki notes
            dictionary_service: Name of dictionary service to use ('youdao' or 'renren')
            include_examples: Whether to include example sentences
            include_phonetic: Whether to include phonetic notation
            include_collins: Whether to include Collins dictionary data
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

        try:
            self.dictionary = DictionaryFactory.get_service(dictionary_service)
        except ValueError as e:
            logger.warning(f"Dictionary service error: {e}. Falling back to Youdao.")
            self.dictionary = DictionaryFactory.get_service('youdao')
            
        self.include_examples = include_examples
        self.include_phonetic = include_phonetic
        self.include_collins = include_collins

    async def transform_to_anki_notes(self, data: List[WordNote]) -> List[Dict[str, str]]:
        """Transform word notes into Anki note format with additional dictionary data."""
        anki_notes = []
        total = len(data)
        
        for i, item in enumerate(data, 1):
            try:
                logger.info(f"Processing word {i}/{total}: {item.word}")
                note = await self._transform_single_item(item)
                if note:
                    anki_notes.append(note)
            except Exception as e:
                logger.error(f"Error transforming item {item}: {e}")
                continue
                
        return anki_notes

    async def _transform_single_item(self, item: WordNote) -> Dict[str, str]:
        """Transform a single word note into Anki note format with dictionary data."""
        # Start with basic note data
        note = {
            "Front": item.word,
            "Back": item.translate
        }
        
        try:
            # Get additional dictionary data
            details = await self.dictionary.lookup_word(item.word)
            if details:
                if self.include_phonetic and details.phonetic:
                    note["Phonetic"] = f"[{details.phonetic}]"
                    
                if self.include_examples and details.examples:
                    note["Examples"] = self.format_examples(details.examples)
                    
                if self.include_collins and details.collins:
                    collins_text = []
                    if 'translations' in details.collins:
                        collins_text.extend(details.collins['translations'])
                    if 'examples' in details.collins:
                        collins_examples = [f"• {ex['en']}\n  {ex['zh']}" 
                                         for ex in details.collins['examples'][:2]]
                        collins_text.extend(collins_examples)
                    note["Collins"] = "\n\n".join(collins_text)
        except Exception as e:
            logger.warning(f"Failed to get dictionary data for {item.word}: {e}")
            
        return note

    def format_examples(self, examples: List[str], max_examples: int = 3) -> str:
        """Format example sentences nicely"""
        if not examples:
            return ""
        formatted = []
        for i, example in enumerate(examples[:max_examples], 1):
            formatted.append(f"{i}. {example}")
        return "\n".join(formatted)