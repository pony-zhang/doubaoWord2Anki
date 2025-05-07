from typing import Dict, Type
from .dictionary_base import DictionaryService
from .youdao_dictionary import YoudaoDictionary
from .renren_dictionary import RenRenDictionary
from .mdx_dictionary import MdxDictionaryService

class DictionaryFactory:
    _services: Dict[str, Type[DictionaryService]] = {
        'youdao': YoudaoDictionary,
        'renren': RenRenDictionary,
        'mdx': MdxDictionaryService
    }

    @classmethod
    def get_service(cls, name: str) -> DictionaryService:
        """Get dictionary service by name
        
        Args:
            name: Name of the dictionary service
            
        Returns:
            Instance of DictionaryService
            
        Raises:
            ValueError: If service name not found
        """
        service_class = cls._services.get(name.lower())
        if not service_class:
            raise ValueError(f"Dictionary service '{name}' not found")
        
        return service_class()

    @classmethod
    def register_service(cls, name: str, service_class: Type[DictionaryService]):
        """Register a new dictionary service
        
        Args:
            name: Name for the service
            service_class: Class implementing DictionaryService
        """
        cls._services[name.lower()] = service_class