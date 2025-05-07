import aiohttp
import asyncio
import backoff
from typing import Dict, Any, Optional, List
import logging
from src.core.interfaces import DataFetcher
from ..core.models import WordNote, ApiResponse, WordNotesResponse
from ..config import settings

logger = logging.getLogger(__name__)

class RequestError(Exception):
    """Custom exception for request errors"""
    pass

class HTTPFetcher(DataFetcher):
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        format: str = 'json'
    ):
        """Initialize HTTP fetcher with configuration"""
        self.format = format.lower()
        # Use the appropriate endpoint based on format
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = (settings.api.doubao.csvendpoint 
                           if self.format == 'csv' 
                           else settings.api.doubao.jsonendpoint)
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = None
        
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

    async def _parse_csv_response(self, content: str) -> List[WordNote]:
        """Parse CSV response into WordNote objects"""
        import csv
        from io import StringIO
        
        # logger.debug("Parsing CSV content",content)

        word_notes = []
        csv_file = StringIO(content.lstrip('\ufeff'))  # Remove BOM if present
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            sentences = row.get('sentences', '').split('\n') if row.get('sentences') else []
            word_note = WordNote(
                source_lang=settings.language.source,
                target_lang=settings.language.target,
                word=row.get('word', ''),
                translate=row.get('translation', ''),
                phonetic=row.get('phonetic', ''),
                sentences=sentences
            )
            word_notes.append(word_note)
            
        return word_notes

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3
    )
    async def _request(
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
                
                if self.format == 'csv':
                    content = await response.text()
                    return await self._parse_csv_response(content)
                
                data = await response.json()
                api_response = ApiResponse(**data)
                
                if api_response.code != 0:
                    error_msg = f"API Error {api_response.code}: {api_response.msg}"
                    logger.error(error_msg)
                    raise RequestError(error_msg)
                
                if not api_response.data:
                    logger.warning("No data in API response")
                    return []
                
                try:
                    word_notes_response = WordNotesResponse(**api_response.data)
                    return word_notes_response.word_notes
                except Exception as e:
                    logger.error(f"Failed to parse word notes: {e}")
                    return []

        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

    async def fetch_data(self, **kwargs) -> List[WordNote]:
        """Fetch word notes from API"""
        params = kwargs.get('params')
        return await self._request("GET", params=params)

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