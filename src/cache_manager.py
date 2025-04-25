import json
import os
from typing import List, Dict, Any, Set
from datetime import datetime
from pathlib import Path
from .config import WordNote

class CacheManager:
    def __init__(self, cache_file: str = "word_cache.json"):
        """Initialize cache manager
        
        Args:
            cache_file: Path to cache file, relative to user's home directory
        """
        self.cache_file = os.path.expanduser(f"~/Downloads/doubao/{cache_file}")
        self._ensure_cache_dir()
        self.cached_words: Set[str] = self._load_cache()

    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        cache_dir = os.path.dirname(self.cache_file)
        os.makedirs(cache_dir, exist_ok=True)

    def _load_cache(self) -> Set[str]:
        """Load cached words from file"""
        if not os.path.exists(self.cache_file):
            return set()
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('words', []))
        except Exception as e:
            print(f"Error loading cache: {e}")
            return set()

    def save_cache(self, words: List[WordNote]):
        """Save words to cache
        
        Args:
            words: List of word notes to cache
        """
        # Add new words to cache
        for word in words:
            self.cached_words.add(word.word)

        # Save to file
        cache_data = {
            'last_updated': datetime.now().isoformat(),
            'words': list(self.cached_words)
        }
        
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def filter_new_words(self, words: List[WordNote]) -> List[WordNote]:
        """Filter out already cached words
        
        Args:
            words: List of word notes to filter
            
        Returns:
            List of new word notes not in cache
        """
        return [word for word in words if word.word not in self.cached_words]