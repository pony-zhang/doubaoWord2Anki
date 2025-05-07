import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from src.fetchers.http import HTTPFetcher
from src.middleware.pipeline import MiddlewarePipeline
from src.middleware.dictionary_enhancement import DictionaryEnhancementMiddleware
from src.middleware.field_mapping import FieldMappingMiddleware
from src.exporters.anki_exporter import AnkiExporter

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Example demonstrating the pipeline architecture"""
    # Initialize components
    fetcher = HTTPFetcher()
    
    # Create pipeline
    pipeline = MiddlewarePipeline()
    
    # Add middleware components
    pipeline.add_middleware(DictionaryEnhancementMiddleware(
        dictionary_service='youdao',
        include_examples=True,
        include_phonetic=True
    ))
    
    pipeline.add_middleware(FieldMappingMiddleware({
        "Front": "word",
        "Back": "translate",
        "Phonetic": "phonetic",
        "Examples": "examples"
    }))
    
    exporter = AnkiExporter()

    # Fetch data
    async with fetcher:
        words = await fetcher.fetch_data()
    
    # Process through pipeline
    notes = await pipeline.process(words)
    
    # Export to Anki
    success = await exporter.export(
        notes,
        deck_name="Vocabulary",
        model_name="Basic"
    )
    
    print("Import completed successfully" if success else "Import failed")

if __name__ == "__main__":
    asyncio.run(main())