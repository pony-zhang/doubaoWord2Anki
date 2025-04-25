import aiohttp
import re
from typing import Optional, List
from .dictionary_base import DictionaryService, WordDetail
from ..config import settings

class YoudaoDictionary(DictionaryService):
    def __init__(self):
        self.base_url = settings.api.dictionaries.youdao.endpoint
        self.headers = {
            "User-Agent": settings.http.headers.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml"
        }

    async def lookup_word(self, word: str) -> Optional[WordDetail]:
        """Look up a word in Youdao Dictionary using simple string parsing"""
        url = f"{self.base_url}/{word}/#keyfrom={settings.api.dictionaries.collins.keyfrom}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    html = await response.text()
                    
                    # Extract phonetic using regex
                    phonetic = None
                    phonetic_match = re.search(r'<span class="phonetic">\[(.*?)\]</span>', html)
                    if phonetic_match:
                        phonetic = phonetic_match.group(1)
                    
                    # Extract basic definition
                    definition = None
                    trans_match = re.search(r'<div class="trans-container">(.*?)</div>', html, re.DOTALL)
                    if trans_match:
                        # Extract definitions from li elements
                        defs = re.findall(r'<li>(.*?)</li>', trans_match.group(1))
                        definition = '\n'.join([d.strip() for d in defs if d.strip()])
                    
                    # Extract examples
                    examples = await self.get_examples(word)
                    
                    # Extract Collins data if available
                    collins_data = None
                    collins_section = re.search(r'<div id="authTrans".*?>(.*?)</div>', html, re.DOTALL)
                    if collins_section:
                        collins_data = self._parse_collins_data(collins_section.group(1))
                    
                    return WordDetail(
                        word=word,
                        phonetic=phonetic,
                        definition=definition,
                        examples=examples,
                        collins=collins_data
                    )
                    
        except Exception as e:
            print(f"Error looking up word in Youdao: {e}")
            return None

    def _parse_collins_data(self, collins_html: str) -> dict:
        """Parse Collins dictionary section using regex"""
        result = {
            'translations': [],
            'examples': []
        }
        
        # Extract translations
        translations = re.findall(r'<div class="collinsMajorTrans">(.*?)</div>', collins_html)
        result['translations'] = [t.strip() for t in translations if t.strip()]
        
        # Extract examples
        example_blocks = re.finditer(r'<p class="examples-sentences">(.*?)</p>.*?<p class="example-via">(.*?)</p>', collins_html, re.DOTALL)
        for match in example_blocks:
            result['examples'].append({
                'en': match.group(1).strip(),
                'zh': match.group(2).strip()
            })
        
        return result

    async def get_examples(self, word: str) -> List[str]:
        """Get example sentences from Youdao using regex"""
        url = f"{self.base_url}/{word}"
        examples = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    html = await response.text()
                    
                    # Extract examples using regex
                    example_matches = re.findall(r'<p class="example-sentences">(.*?)</p>', html)
                    examples = [e.strip() for e in example_matches if e.strip()]
                            
        except Exception as e:
            print(f"Error getting examples from Youdao: {e}")
            
        return examples[:5]  # Return up to 5 examples