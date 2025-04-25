import json
import requests
from typing import Dict, Any, List
from loguru import logger
from .config import settings

class AnkiExporter:
    def __init__(self, connect_url: str = None):
        self.connect_url = connect_url or settings.anki_connect_url

    async def add_notes(self, deck_name: str, model_name: str, notes: List[Dict[str, Any]]) -> bool:
        """Add notes to Anki through AnkiConnect."""
        try:
            payload = {
                "action": "addNotes",
                "version": 6,
                "params": {
                    "notes": [{
                        "deckName": deck_name,
                        "modelName": model_name,
                        "fields": note,
                        "options": {
                            "allowDuplicate": False
                        },
                    } for note in notes]
                }
            }
            response = requests.post(self.connect_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get("error"):
                logger.error(f"Anki error: {result['error']}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to add notes to Anki: {e}")
            return False