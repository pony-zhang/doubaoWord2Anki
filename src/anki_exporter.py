import json
import aiohttp
import genanki
import os
from typing import Dict, Any, List, Optional
from loguru import logger
from .config import settings

class AnkiExporter:
    def __init__(self, anki_connect_url: str = None):
        """Initialize AnkiExporter
        
        Args:
            anki_connect_url: URL for AnkiConnect API, defaults to config value
        """
        self.anki_connect_url = anki_connect_url or settings.anki_connect_url
        
        # Default note model for vocabulary
        self.model = genanki.Model(
            1607392319,  # Random model ID
            "Doubao Vocabulary",
            fields=[
                {'name': 'Front'},
                {'name': 'Back'},
            ],
            templates=[{
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
            }]
        )

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
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.anki_connect_url, json=payload) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
                    if result.get("error"):
                        logger.error(f"Anki error: {result['error']}")
                        return False
                    
                    return True
            
        except Exception as e:
            logger.error(f"Failed to add notes to Anki: {e}")
            return False

    def export_to_apkg(
        self,
        notes: List[Dict[str, str]],
        output_path: str,
        deck_name: Optional[str] = None
    ) -> bool:
        """Export notes to .apkg file
        
        Args:
            notes: List of notes (each with Front and Back fields)
            output_path: Path where to save the .apkg file
            deck_name: Name of the deck (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create deck
            deck = genanki.Deck(
                2059400110,  # Random deck ID
                deck_name or "Doubao Vocabulary"
            )

            # Add notes to deck
            for note_fields in notes:
                note = genanki.Note(
                    model=self.model,
                    fields=[note_fields['Front'], note_fields['Back']]
                )
                deck.add_note(note)

            # Create package and save
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
            package = genanki.Package(deck)
            package.write_to_file(output_path)
            
            logger.success(f"Successfully exported deck to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export deck: {e}")
            return False