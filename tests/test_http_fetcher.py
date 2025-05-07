import pytest
import pytest_asyncio
import json
import logging
from src.fetchers.http import HTTPFetcher
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MOCK_CSV_URL = "https://mock-api.test/csv"
MOCK_JSON_URL = "https://mock-api.test/json"

@pytest_asyncio.fixture
def mock_settings():
    with patch('src.fetchers.http.settings') as mock_settings:
        mock_settings.api.doubao.cookie = "test_cookie"
        mock_settings.api.doubao.csvendpoint = MOCK_CSV_URL
        mock_settings.api.doubao.jsonendpoint = MOCK_JSON_URL
        mock_settings.language.source = "en"
        mock_settings.language.target = "zh"
        mock_settings.language.default = "en"
        mock_settings.http.headers.user_agent = "Test User Agent"
        yield mock_settings

@pytest_asyncio.fixture
async def fetcher():
    """Create an HTTPFetcher instance for testing"""
    return HTTPFetcher(timeout=30, max_retries=3)

@pytest.mark.asyncio
async def test_fetch_data(fetcher):
    """Test fetching word data and log detailed information"""
    logger.info("=== Starting HTTP Request Test ===")
    logger.info(f"Base URL: {fetcher.base_url}")
    logger.debug(f"Headers: {json.dumps(fetcher._get_headers(), indent=2, ensure_ascii=False)}")
    
    try:
        # Add some test parameters
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

@pytest.mark.asyncio
async def test_csv_format_fetch(mock_settings):
    """Test fetching data in CSV format"""
    csv_content = '''word,translation,phonetic,mastered,sentences
symphony,"n. 交响乐","英 [ˈsɪmfəni]",No,"Symphony musicians cannot necessarily sight-read."
sanguine,"adj. 乐观的","英 [ˈsæŋɡwɪn]",No,"They are less sanguine about the company's prospects."'''
    
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=csv_content)
    mock_response.raise_for_status = AsyncMock()
    
    mock_session = AsyncMock()
    mock_session.request.return_value.__aenter__.return_value = mock_response
    mock_session.closed = False
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        fetcher = HTTPFetcher(format='csv')
        async with fetcher:
            words = await fetcher.fetch_data()
            
        assert len(words) == 2
        assert words[0].word == "symphony"
        assert words[0].translate == "n. 交响乐"
        assert words[0].phonetic == "英 [ˈsɪmfəni]"
        assert words[0].mastered is False
        assert "Symphony musicians cannot necessarily sight-read." in words[0].sentences

@pytest.mark.asyncio
async def test_json_format_fetch(mock_settings):
    """Test fetching data in JSON format"""
    json_data = {
        "code": 0,
        "msg": "",
        "data": {
            "word_notes": [
                {
                    "source_lang": "en",
                    "target_lang": "zh",
                    "word": "symphony",
                    "translate": "交响乐"
                }
            ]
        }
    }
    
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=json_data)
    mock_response.raise_for_status = AsyncMock()
    
    mock_session = AsyncMock()
    mock_session.request.return_value.__aenter__.return_value = mock_response
    mock_session.closed = False
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        fetcher = HTTPFetcher(format='json')
        async with fetcher:
            words = await fetcher.fetch_data()
            
        assert len(words) == 1
        assert words[0].word == "symphony"
        assert words[0].translate == "交响乐"

