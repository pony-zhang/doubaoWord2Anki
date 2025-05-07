import pytest
import pytest_asyncio
import json
import logging
from src.fetchers.http import HTTPFetcher

# 配置日志格式
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@pytest_asyncio.fixture
async def fetcher():
    """创建一个HTTPFetcher实例用于测试"""
    return HTTPFetcher(timeout=30, max_retries=3)

@pytest.mark.asyncio
async def test_fetch_data(fetcher):
    """测试获取单词数据并记录详细信息"""
    logger.info("=== Starting HTTP Request Test ===")
    logger.info(f"Base URL: {fetcher.base_url}")
    logger.debug(f"Headers: {json.dumps(fetcher._get_headers(), indent=2, ensure_ascii=False)}")
    
    try:
        # 添加一些测试参数
        params = {
            "page": 1,
            "limit": 10
        }
        logger.info(f"Request Parameters: {json.dumps(params, indent=2, ensure_ascii=False)}")
        
        result = await fetcher.fetch_data(params=params)
        logger.info("=== API Response ===")
        if result:
            logger.info(f"Number of word notes received: {len(result)}")
            for note in result:
                logger.debug(f"Word Note: {json.dumps(note.__dict__, indent=2, ensure_ascii=False)}")
        else:
            logger.warning("No word notes returned")
    
    except Exception as e:
        logger.error("=== Error Occurred ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
    finally:
        await fetcher.close()

