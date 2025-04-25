import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from loguru import logger
from .config import settings, ApiResponse, WordNote, WordNotesResponse
import backoff

class RequestError(Exception):
    """Custom exception for request errors"""
    pass

class HTTPClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize HTTP client with configuration"""
        self.base_url = base_url or settings.api.doubao.endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = None
        
        # Validate required settings
        if not settings.api.doubao.cookie:
            raise ValueError("Cookie not set in config.yaml under api.doubao.cookie")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._session

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Cookie": settings.api.doubao.cookie,
            "User-Agent": settings.http.headers.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3
    )
    async def request(
        self,
        method: str,
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[WordNote]:
        """Make HTTP request with automatic retries and error handling"""
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint}".rstrip('/')

        # Required parameters for the API
        default_params = {
            "language": settings.language.default,
            "source_lang": settings.language.source,
            "target_lang": settings.language.target
        }

        if params:
            default_params.update(params)

        logger.debug(f"Making request to {url} with params: {default_params}")

        try:
            async with session.request(
                method,
                url,
                params=default_params,
                json=json,
                headers=self._get_headers(),
                **kwargs
            ) as response:
                response.raise_for_status()
                data = await response.json()
                logger.debug(f"API Response: {data}")
                
                # Validate response structure
                api_response = ApiResponse(**data)
                
                # Handle API errors
                if api_response.code != 0:  # Non-zero code indicates error
                    error_msg = f"API Error {api_response.code}: {api_response.msg}"
                    logger.error(error_msg)
                    raise RequestError(error_msg)
                
                # Validate the data contains word notes
                if not api_response.data:
                    logger.warning("No data in API response")
                    return []
                
                try:
                    word_notes_response = WordNotesResponse(**api_response.data)
                    return word_notes_response.word_notes
                except Exception as e:
                    logger.error(f"Failed to parse word notes: {e}")
                    return []

        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise RequestError(f"Request failed: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    async def get_data(
        self,
        params: Optional[Dict[str, Any]] = None
    ) -> List[WordNote]:
        """Get word notes from API
        
        Args:
            params: Additional parameters to pass to the API
        
        Returns:
            List of word notes
        """
        return await self.request("GET", params=params)

    async def close(self):
        """Close the client session"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        """Support async context manager"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on exit"""
        await self.close()