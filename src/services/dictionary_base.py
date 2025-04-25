from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class WordDetail:
    """Word details from dictionary"""
    word: str
    phonetic: Optional[str] = None
    definition: Optional[str] = None
    examples: Optional[list[str]] = None
    collins: Optional[Dict[str, Any]] = None
    additional_info: Optional[Dict[str, Any]] = None

class DictionaryService(ABC):
    """Abstract base class for dictionary services"""
    
    @abstractmethod
    async def lookup_word(self, word: str) -> Optional[WordDetail]:
        """Look up a word in the dictionary
        
        Args:
            word: The word to look up
            
        Returns:
            WordDetail object if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_examples(self, word: str) -> list[str]:
        """Get example sentences for a word
        
        Args:
            word: The word to get examples for
            
        Returns:
            List of example sentences
        """
        pass