from typing import List, Type
from ..core.interfaces import DataMiddleware
from ..core.models import WordNote
import logging
logger = logging.getLogger(__name__)

class MiddlewarePipeline:
    """Pipeline for processing data through multiple middleware components"""
    
    def __init__(self):
        self.middlewares: List[DataMiddleware] = []
        
    def add_middleware(self, middleware: DataMiddleware) -> 'MiddlewarePipeline':
        """Add a middleware to the pipeline
        
        Args:
            middleware: Middleware instance to add
            
        Returns:
            Self for chaining
        """
        self.middlewares.append(middleware)
        return self
        
    async def process(self, data: List[WordNote]) -> List[WordNote]:
        """Process data through all registered middleware
        
        Args:
            data: Input data to process
            
        Returns:
            Processed data
        """
        current_data = data
        
        for middleware in self.middlewares:
            try:
                logger.debug(f"Processing through {middleware.__class__.__name__}")
                current_data = await middleware.process(current_data)
            except Exception as e:
                logger.error(f"Error in middleware {middleware.__class__.__name__}: {e}")
                raise
                
        return current_data