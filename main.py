import asyncio
import os
from datetime import datetime
import logging as logger
from src.fetchers.http import HTTPFetcher
from src.middleware.pipeline import MiddlewarePipeline
from src.middleware.dictionary_enhancement import DictionaryEnhancementMiddleware
from src.middleware.field_mapping import FieldMappingMiddleware
from src.exporters.anki_exporter import AnkiExporter
from src.cache_manager import CacheManager
from src.config import settings

async def main():
    """Main function to fetch words and export to Anki using the pipeline architecture"""
    try:
        # Initialize pipeline components
        fetcher = HTTPFetcher(
            timeout=settings.http.timeout,
            max_retries=settings.http.max_retries
        )
        
        # Create middleware pipeline
        pipeline = MiddlewarePipeline()
        pipeline.add_middleware(DictionaryEnhancementMiddleware(
            dictionary_service='youdao',
            include_examples=True,
            include_phonetic=True,
            include_collins=True
        ))
        pipeline.add_middleware(FieldMappingMiddleware(
            field_mappings=settings.anki.field_mappings
        ))
        
        exporter = AnkiExporter(anki_connect_url=settings.anki.connect_url)
        cache_manager = CacheManager(
            cache_file=settings.cache.file
        ) if settings.cache.enabled else None

        # Fetch word data
        logger.info("Fetching words from Doubao...")
        async with fetcher:
            word_data = await fetcher.fetch_data()
                
        if not word_data:
            logger.warning("No word data received")
            return

        # Filter out cached words if enabled
        if cache_manager and settings.cache.enabled:
            new_words = cache_manager.filter_new_words(word_data)
            if not new_words:
                logger.info("No new words to process")
                return
            logger.info(f"Found {len(new_words)} new words")
            words_to_process = new_words
        else:
            words_to_process = word_data

        # Process data through pipeline
        logger.info(f"Processing {len(words_to_process)} words through pipeline...")
        processed_notes = await pipeline.process(words_to_process)

        # Export to Anki
        logger.info(f"Exporting {len(processed_notes)} notes to Anki...")
        
        # Export via AnkiConnect
        success = await exporter.export(
            processed_notes,
            deck_name=settings.anki.deck_name,
            model_name=settings.anki.model_name
        )

        if success:
            logger.success(f"Successfully exported {len(processed_notes)} words to Anki!")
            
            # Export backup .apkg file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.expanduser(f"~/Downloads/doubao_vocab_{timestamp}.apkg")
            
            await exporter.export(
                processed_notes,
                output_path=output_path,
                deck_name=settings.anki.deck_name
            )
            
            # Update cache with new words if enabled
            if cache_manager and settings.cache.enabled:
                cache_manager.save_cache(words_to_process)
                logger.info("Cache updated with new words")
        else:
            logger.error("Failed to export notes to Anki")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    logger.info("Starting Doubao Word to Anki import process...")
    asyncio.run(main())
