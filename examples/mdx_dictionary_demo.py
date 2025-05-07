import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from src.services.mdx_dictionary import MdxDictionaryService
import os
import logging

logger = logging.getLogger(__name__)

async def main():
    # 设置MDX词典文件路径
    mdx_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "英语词根词源记忆词典.mdx")
    MdxDictionaryService.set_mdx_path(mdx_path)
    
    # 获取MDX词典服务实例
    dictionary = MdxDictionaryService()
    
    # 要查询的单词列表
    words = ["hello", "world", "python", "computer"]
    
    # 查询每个单词
    for word in words:
        print(f"\n{'='*40}\n正在查询单词: {word}\n{'='*40}")
        result = await dictionary.lookup_word(word)
        
        if result:
            print("\n基本信息:")
            print(f"单词: {result.word}")
            
            if result.additional_info.get('part_of_speech'):
                print(f"词性: {result.additional_info['part_of_speech']}")
                
            if result.additional_info.get('word_root'):
                print("\n基本释义:")
                print(result.additional_info['word_root'])
                
            if result.examples:
                print("\n例句:")
                for i, example in enumerate(result.examples, 1):
                    print(f"{i}. {example}")
                    
            if result.additional_info.get('etymology'):
                print("\n词源:")
                print(result.additional_info['etymology'])
        else:
            print(f"未在MDX词典中找到单词 '{word}'")

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())