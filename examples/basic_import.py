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
    fetcher = HTTPFetcher(format='csv')
    
    # Create pipeline
    pipeline = MiddlewarePipeline()
    
    # # Add middleware components
    # pipeline.add_middleware(DictionaryEnhancementMiddleware(
    #     dictionary_service='youdao',
    #     include_examples=True,
    #     include_phonetic=True
    # ))
    
    # pipeline.add_middleware(FieldMappingMiddleware({
    #     "Front": "word",
    #     "Back": "translation",  # Changed from 'translate' to match CSV format
    #     "Phonetic": "phonetic",
    #     "Examples": "sentences"  # Changed from 'examples' to match CSV format
    # }))
    
    exporter = AnkiExporter()

    # Fetch data
    async with fetcher:
        words = await fetcher.fetch_data()
        logger.info(f"Fetched {len(words)} words from the source.")
        for word in words:
            info = (
                f"Word: {word.word}, "
                f"Translation: {word.translate}, "
                f"Source: {word.source_lang}→{word.target_lang}, "
                f"Phonetic: {word.phonetic or 'N/A'}, "
            )
            if word.examples:
                info += f", Examples: {' | '.join(word.examples)}"
            if word.sentences:
                info += f", Sentences: {' | '.join(word.sentences)}"
            if word.collins or word.additional_info:
                info += f", Extra: {word.collins or word.additional_info}"
            logger.debug(info)
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