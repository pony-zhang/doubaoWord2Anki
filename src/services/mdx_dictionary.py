from typing import Optional
import asyncio
from pathlib import Path
from pyglossary.glossary import Glossary
from .dictionary_base import DictionaryService, WordDetail
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class MdxDictionaryService(DictionaryService):
    """Service for querying local MDX dictionary files"""
    
    _mdx_path: str = None
    
    @classmethod
    def set_mdx_path(cls, path: str):
        """Set the path to MDX dictionary file"""
        cls._mdx_path = path
    
    def __init__(self):
        """Initialize MDX dictionary service"""
        if not self._mdx_path:
            raise ValueError("MDX dictionary path not set. Call set_mdx_path() first.")
            
        self.mdx_path = Path(self._mdx_path)
        if not self.mdx_path.exists():
            raise FileNotFoundError(f"MDX file not found: {self._mdx_path}")
            
        # 初始化 PyGlossary
        Glossary.init()
        self.glos = Glossary()
        self.glos.config = {
            'lower': True,
            'skip_resources': True,
            'html': True,
        }
        
        # 加载词典文件
        success = self.glos.read(str(self._mdx_path))
        if not success:
            raise RuntimeError(f"Failed to load MDX file: {self._mdx_path}")
        
        logger.info(f"Successfully loaded MDX dictionary: {self._mdx_path}")

    def _parse_definition(self, raw_def: str) -> tuple[Optional[str], Optional[str], list[str], dict]:
        """Parse the raw definition to extract structured information
        
        Returns:
            Tuple of (phonetic, definition, examples, additional_info)
        """
        try:
            if not raw_def:
                return None, None, [], {}
                
            soup = BeautifulSoup(raw_def, 'html.parser')
            additional_info = {}
            
            # 找到词源和词根记忆部分
            etymology_title = soup.find('b', text=lambda t: t and '词源' in t)
            root_title = soup.find('b', text=lambda t: t and '词根记忆' in t)
            
            # 提取词源信息
            if etymology_title:
                etymology_text = ''
                for sibling in etymology_title.next_siblings:
                    if isinstance(sibling, str):
                        etymology_text += sibling
                    elif hasattr(sibling, 'get_text'):
                        if sibling.name == 'b' and '词根记忆' in sibling.get_text():
                            break
                        etymology_text += sibling.get_text()
                
                if etymology_text.strip():
                    additional_info['etymology'] = etymology_text.strip()
            
            # 提取词根记忆信息
            examples = []
            if root_title:
                root_text = ''
                for sibling in root_title.next_siblings:
                    if isinstance(sibling, str):
                        root_text += sibling
                    elif hasattr(sibling, 'get_text'):
                        root_text += sibling.get_text()
                
                root_text = root_text.strip()
                if root_text:
                    # 提取词性
                    pos_match = False
                    for pos in ['n.', 'v.', 'adj.', 'adv.', 'int.', 'prep.', 'pron.', 'conj.']:
                        if root_text.startswith(pos):
                            additional_info['part_of_speech'] = pos
                            root_text = root_text[len(pos):].strip()
                            pos_match = True
                            break
                    
                    # 处理颜色标记的词性
                    if not pos_match:
                        color_pos = soup.find('font', color='red')
                        if color_pos and color_pos.string:
                            pos = color_pos.string.strip()
                            if pos.endswith('.'):
                                additional_info['part_of_speech'] = pos
                                root_text = root_text.replace(pos, '').strip()
                    
                    # 分离释义和例句
                    if '.' in root_text:
                        parts = [p.strip() for p in root_text.split('.') if p.strip()]
                        if parts:
                            main_def = parts[0]
                            additional_info['word_root'] = main_def
                            examples = parts[1:]
                    else:
                        additional_info['word_root'] = root_text
            
            # 如果有 word_root，返回它作为主要释义
            definition = additional_info.get('word_root', raw_def)
            return None, definition, examples, additional_info
            
        except Exception as e:
            logger.error(f"Error parsing definition: {e}")
            return None, raw_def, [], {'raw_html': raw_def}

    async def lookup_word(self, word: str) -> Optional[WordDetail]:
        """Look up a word in the MDX dictionary"""
        raw_result = await asyncio.get_event_loop().run_in_executor(
            None, self._lookup_word_sync, word
        )
        
        if not raw_result:
            return None
        
        # 解析原始结果
        key, raw_def = raw_result
        phonetic, definition, examples, additional_info = self._parse_definition(raw_def)
            
        return WordDetail(
            word=key,
            definition=definition,
            phonetic=phonetic,
            examples=examples,
            collins=None,
            additional_info=additional_info
        )
        
    def _lookup_word_sync(self, word: str) -> Optional[tuple[str, str]]:
        """Synchronous word lookup implementation
        
        Returns:
            Tuple of (word, definition) if found, None otherwise
        """
        try:
            word = word.lower()
            # 直接遍历词典条目
            for entry in self.glos:
                if not hasattr(entry, 'defi'):  # 跳过无效条目
                    continue
                    
                # 检查主词条
                if hasattr(entry, 's_word') and entry.s_word and entry.s_word.lower() == word:
                    return entry.s_word, entry.defi
                
                # 检查词条变体
                if hasattr(entry, 'l_word') and entry.l_word:
                    # 如果是列表，检查每个变体
                    if isinstance(entry.l_word, (list, tuple)):
                        for variant in entry.l_word:
                            if variant.lower() == word:
                                return variant, entry.defi
                    # 如果是字符串，直接检查
                    elif isinstance(entry.l_word, str) and entry.l_word.lower() == word:
                        return entry.l_word, entry.defi
            
            return None
            
        except Exception as e:
            logger.error(f"Error looking up word '{word}': {e}")
            return None

    async def get_examples(self, word: str) -> list[str]:
        """Get example sentences for a word"""
        result = await self.lookup_word(word)
        if result and result.examples:
            return result.examples
        return []