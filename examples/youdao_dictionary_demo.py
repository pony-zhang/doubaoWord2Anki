import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from src.services.youdao_dictionary import YoudaoDictionary

async def main():
    # 创建有道词典服务实例
    dictionary = YoudaoDictionary()
    
    # 要查询的单词列表
    words = ["hello", "world", "python"]
    
    # 查询每个单词
    for word in words:
        print(f"\n正在查询单词: {word}")
        result = await dictionary.lookup_word(word)
        
        if result:
            print("查询结果:")
            print(f"单词: {result.word}")
            print(f"音标: {result.phonetic or '无'}")
            print(f"释义: {result.definition or '无'}")
            
            if result.examples:
                print("\n例句:")
                for i, example in enumerate(result.examples, 1):
                    print(f"{i}. {example}")
            
            if result.collins:
                print("\nCollins词典数据:")
                for i, trans in enumerate(result.collins.get('translations', []), 1):
                    print(f"{i}. {trans}")
                
                if result.collins.get('examples'):
                    print("\nCollins例句:")
                    for i, example in enumerate(result.collins['examples'], 1):
                        print(f"{i}. 英文: {example['en']}")
                        print(f"   中文: {example['zh']}")
        else:
            print(f"未找到单词 '{word}' 的释义")

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())