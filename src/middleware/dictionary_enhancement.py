from typing import List, Dict, Any
from ..core.interfaces import DataMiddleware
from ..core.models import WordNote
from ..services.dictionary_factory import DictionaryFactory
import logging

logger = logging.getLogger(__name__)

class DictionaryEnhancementMiddleware(DataMiddleware):
    """Middleware to enrich word data with dictionary lookups"""
    
    def __init__(
        self,
        dictionary_service: str = 'youdao',
        include_examples: bool = True,
        include_phonetic: bool = True,
        include_collins: bool = True
    ):
        """Initialize dictionary enhancement middleware
        
        Args:
            dictionary_service: Name of dictionary service to use
            include_examples: Whether to include example sentences
            include_phonetic: Whether to include phonetic notation
            include_collins: Whether to include Collins dictionary data
        """
        try:
            self.dictionary = DictionaryFactory.get_service(dictionary_service)
        except ValueError as e:
            logger.warning(f"Dictionary service error: {e}. Falling back to Youdao.")
            self.dictionary = DictionaryFactory.get_service('youdao')
            
        self.include_examples = include_examples
        self.include_phonetic = include_phonetic
        self.include_collins = include_collins

    async def process(self, data: List[WordNote]) -> List[WordNote]:
        """Process word notes by adding dictionary data
        
        Args:
            data: List of word notes to enhance
            
        Returns:
            Enhanced word notes
        """
        enhanced_notes = []
        total = len(data)
        
        for i, note in enumerate(data, 1):
            try:
                logger.info(f"Enhancing word {i}/{total}: {note.word}")
                enhanced_note = await self._enhance_note(note)
                enhanced_notes.append(enhanced_note)
            except Exception as e:
                logger.error(f"Error enhancing word {note.word}: {e}")
                enhanced_notes.append(note)  # Keep original note on error
                
        return enhanced_notes

    async def _enhance_note(self, note: WordNote) -> WordNote:
        """Enhance a single word note with dictionary data"""
        try:
            details = await self.dictionary.lookup_word(note.word)
            if details:
                if self.include_phonetic:
                    note.phonetic = details.phonetic
                    
                if self.include_examples:
                    note.examples = details.examples
                    
                if self.include_collins:
                    note.collins = details.collins
                    
        except Exception as e:
            logger.warning(f"Failed to get dictionary data for {note.word}: {e}")
            
        return note