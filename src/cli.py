import asyncio
import click
from loguru import logger
from .http_client import HTTPClient
from .transformer import DataTransformer
from .anki_exporter import AnkiExporter
from .config import settings

@click.command()
@click.option('--deck-name', required=True, help='Name of the Anki deck to add cards to')
@click.option('--model-name', required=True, help='Name of the Anki note type to use')
@click.option('--endpoint', default='', help='API endpoint to fetch data from')
async def main(deck_name: str, model_name: str, endpoint: str):
    """Import data from API to Anki."""
    try:
        # Initialize components
        client = HTTPClient(endpoint)
        transformer = DataTransformer()
        exporter = AnkiExporter()

        # Fetch data
        logger.info("Fetching data from API...")
        data = await client.get_data()

        # Transform data
        logger.info("Transforming data for Anki...")
        notes = transformer.transform_to_anki_notes(data)

        if not notes:
            logger.warning("No valid notes found to import")
            return

        # Export to Anki
        logger.info(f"Adding {len(notes)} notes to Anki...")
        success = await exporter.add_notes(deck_name, model_name, notes)

        if success:
            logger.success("Successfully imported notes to Anki")
        else:
            logger.error("Failed to import some or all notes to Anki")

    except Exception as e:
        logger.error(f"Error during import process: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(main())