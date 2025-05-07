from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional
from .models import WordNote

class DataFetcher(ABC):
    """Abstract base class for data fetchers"""
    
    @abstractmethod
    async def fetch_data(self, **kwargs) -> List[WordNote]:
        """Fetch data from source
        
        Args:
            **kwargs: Additional parameters for the fetch operation
            
        Returns:
            List of word notes
        """
        pass

class DataMiddleware(ABC):
    """Abstract base class for data processing middleware"""
    
    @abstractmethod
    async def process(self, data: List[WordNote]) -> List[WordNote]:
        """Process data through the middleware
        
        Args:
            data: Input data to process
            
        Returns:
            Processed data
        """
        pass

class DataExporter(ABC):
    """Abstract base class for data exporters"""
    
    @abstractmethod
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> bool:
        """Export data to destination
        
        Args:
            data: Data to export
            **kwargs: Additional export parameters
            
        Returns:
            True if export successful, False otherwise
        """
        pass