import aiohttp
import asyncio
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel
from loguru import logger
from .config import settings
import backoff

class RequestError(Exception):
    """Custom exception for request errors"""
    pass

class ResponseModel(BaseModel):
    """Response data model"""
    code: int
    msg: str
    data: Optional[Dict[str, Any]]

class HTTPClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize HTTP client with configuration

        Args:
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url or settings.api_endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = None

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
            "Cookie": settings.doubao_cookie,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
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
    ) -> Dict[str, Any]:
        """Make HTTP request with automatic retries and error handling

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json: JSON body data
            **kwargs: Additional arguments for request

        Returns:
            Response data as dictionary

        Raises:
            RequestError: If request fails after retries
        """
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint}".rstrip('/')

        default_params = {
            "language": settings.language,
            "source_lang": settings.source_lang,
            "target_lang": settings.target_lang
        }

        # Merge default params with custom params
        if params:
            default_params.update(params)

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
                
                # Validate response structure
                response_model = ResponseModel(**data)
                if response_model.code != 0:  # Assuming 0 is success code
                    raise RequestError(f"API Error: {response_model.msg}")
                
                logger.debug(f"Request successful: {url}")
                return response_model.data or {}

        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise RequestError(f"Request failed: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    async def get_data(
        self,
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convenience method for GET requests"""
        return await self.request("GET", endpoint, params=params)

    async def post_data(
        self,
        endpoint: str = "",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convenience method for POST requests"""
        return await self.request("POST", endpoint, json=data, params=params)

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