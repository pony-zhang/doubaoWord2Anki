# doubaoWord2Anki

A Python tool for importing word data into Anki flashcards.

## Installation

```bash
pip install .
```

## Requirements

- Python 3.8+
- AnkiConnect plugin installed in Anki
- Running Anki instance with AnkiConnect enabled

## Configuration

1. Copy `.env.example` to `.env`
2. Modify the settings in `.env` to match your setup:
   - `API_ENDPOINT`: The API endpoint to fetch word data from
   - `ANKI_CONNECT_URL`: The URL where AnkiConnect is running (default: http://localhost:8765)
   - `FIELD_MAPPINGS`: JSON mapping of Anki note fields to API data fields

## Usage

### Command Line

```bash
anki-importer --deck-name "My Deck" --model-name "Basic" --endpoint "http://api.example.com/words"
```

### Python API

```python
from doubaoWord2Anki import HTTPClient, DataTransformer, AnkiExporter

# See examples/basic_import.py for a complete example
```

## Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -e .`

## License

MIT