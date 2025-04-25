import asyncio
import os
from datetime import datetime
from loguru import logger
from src.http_client import HTTPClient
from src.transformer import DataTransformer
from src.anki_exporter import AnkiExporter
from src.cache_manager import CacheManager
from src.config import settings

async def main():
    """Main function to fetch words and export to Anki"""
    try:
        # Initialize components with configuration
        async with HTTPClient(
            timeout=settings.http.timeout,
            max_retries=settings.http.max_retries
        ) as client:
            transformer = DataTransformer(
                field_mappings=settings.anki.field_mappings,
                dictionary_service='youdao',  # You can make this configurable
                include_examples=True,
                include_phonetic=True,
                include_collins=True
            )
            exporter = AnkiExporter(anki_connect_url=settings.anki.connect_url)
            cache_manager = CacheManager(
                cache_file=settings.cache.file
            ) if settings.cache.enabled else None

            # Fetch word data from doubao
            logger.info("Fetching words from Doubao...")
            word_data = await client.get_data()
                
            if not word_data:
                logger.warning("No word data received")
                return

            # Filter out already cached words if caching is enabled
            if cache_manager and settings.cache.enabled:
                new_words = cache_manager.filter_new_words(word_data)
                if not new_words:
                    logger.info("No new words to process")
                    return
                logger.info(f"Found {len(new_words)} new words")
                words_to_process = new_words
            else:
                words_to_process = word_data

            # Transform data for Anki with dictionary enrichment
            logger.info(f"Transforming {len(words_to_process)} words for Anki...")
            anki_notes = await transformer.transform_to_anki_notes(words_to_process)

            # Export to Anki via AnkiConnect
            logger.info(f"Exporting {len(anki_notes)} notes to Anki...")
            success = await exporter.add_notes(
                settings.anki.deck_name,
                settings.anki.model_name, 
                anki_notes
            )

            if success:
                logger.success(f"Successfully exported {len(anki_notes)} words to Anki!")
                
                # Export to .apkg file as backup
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.expanduser(f"~/Downloads/doubao_vocab_{timestamp}.apkg")
                
                if exporter.export_to_apkg(anki_notes, output_path, settings.anki.deck_name):
                    logger.success(f"Backup deck exported to {output_path}")
                
                # Update cache with new words if enabled
                if cache_manager and settings.cache.enabled:
                    cache_manager.save_cache(words_to_process)
                    logger.info("Cache updated with new words")
            else:
                logger.error("Failed to export notes to Anki")

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    logger.info("Starting Doubao Word to Anki import process...")
    asyncio.run(main())
