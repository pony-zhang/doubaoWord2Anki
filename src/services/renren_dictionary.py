import aiohttp
import re
from typing import Optional, List
from .dictionary_base import DictionaryService, WordDetail
from ..config import settings

class RenRenDictionary(DictionaryService):
    def __init__(self):
        self.base_url = settings.api.dictionaries.renren.endpoint
        self.headers = {
            "User-Agent": settings.http.headers.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml"
        }

    async def lookup_word(self, word: str) -> Optional[WordDetail]:
        """Look up a word in RenRen Dictionary using simple string parsing"""
        word = word.replace(' ', '%20')
        url = f"{self.base_url}?w={word}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    html = await response.text()
                    
                    if '查不到该词' in html:
                        return None
                    
                    # Extract definition using regex
                    definition = None
                    meanings = re.findall(r'<div class="exp">(.*?)</div>', html)
                    if meanings:
                        definition = '\n'.join([m.strip() for m in meanings if m.strip()])
                    
                    # Get examples
                    examples = await self.get_examples(word)
                    
                    return WordDetail(
                        word=word,
                        definition=definition,
                        examples=examples
                    )
                    
        except Exception as e:
            print(f"Error looking up word in RenRen: {e}")
            return None

    async def get_examples(self, word: str) -> List[str]:
        """Get example sentences from RenRen using regex"""
        word = word.replace(' ', '%20')
        url = f"{self.base_url}?w={word}"
        examples = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    html = await response.text()
                    
                    # Extract English examples using regex
                    example_matches = re.finditer(r'<div class="sent">.*?<div class="en">(.*?)</div>', html, re.DOTALL)
                    examples = [m.group(1).strip() for m in example_matches if m.group(1).strip()]
                            
        except Exception as e:
            print(f"Error getting examples from RenRen: {e}")
            
        return examples[:5]  # Return up to 5 examples