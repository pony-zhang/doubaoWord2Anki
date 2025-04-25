import asyncio
from doubaoWord2Anki import HTTPClient, DataTransformer, AnkiExporter

async def main():
    # Initialize components
    client = HTTPClient("http://api.example.com/words")
    transformer = DataTransformer({
        "Front": "word",
        "Back": "definition"
    })
    exporter = AnkiExporter()

    # Fetch sample data
    data = await client.get_data()
    
    # Transform data to Anki notes format
    notes = transformer.transform_to_anki_notes(data)
    
    # Export to Anki
    success = await exporter.add_notes(
        deck_name="Vocabulary",
        model_name="Basic",
        notes=notes
    )
    
    print("Import completed successfully" if success else "Import failed")

if __name__ == "__main__":
    asyncio.run(main())