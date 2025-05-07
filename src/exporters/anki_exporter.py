import aiohttp
import genanki
import os
from typing import Dict, Any, List, Optional
import logging as logger
from ..core.interfaces import DataExporter
from ..config import settings

class AnkiExporter(DataExporter):
    """Exporter for Anki notes with support for both AnkiConnect and .apkg export"""
    
    def __init__(self, anki_connect_url: str = None):
        """Initialize AnkiExporter
        
        Args:
            anki_connect_url: URL for AnkiConnect API, defaults to config value
        """
        self.anki_connect_url = anki_connect_url or settings.anki.connect_url
        
        # Default note model for vocabulary
        self.model = genanki.Model(
            1607392319,  # Random model ID
            "Doubao Vocabulary",
            fields=[
                {'name': 'Front'},
                {'name': 'Back'},
                {'name': 'Phonetic'},
                {'name': 'Examples'},
                {'name': 'Collins'}
            ],
            templates=[{
                'name': 'Card 1',
                'qfmt': '{{Front}}<br>{{Phonetic}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Back}}<br><br>{{Examples}}<br><br>{{Collins}}',
            }]
        )

    async def create_deck(self, deck_name: str) -> bool:
        """Create a new deck in Anki if it doesn't exist"""
        try:
            payload = {
                "action": "createDeck",
                "version": 6,
                "params": {
                    "deck": deck_name
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.anki_connect_url, json=payload) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
                    if result.get("error"):
                        logger.error(f"Failed to create deck: {result['error']}")
                        return False
                    
                    logger.info(f"Created deck: {deck_name}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error creating deck: {e}")
            return False

    async def export(self, notes: List[Dict[str, Any]], **kwargs) -> bool:
        """Export notes to Anki through AnkiConnect
        
        Args:
            notes: List of notes to export
            **kwargs: Additional parameters including:
                - deck_name: Name of the deck to export to
                - model_name: Name of the note model to use
                - output_path: Optional path for .apkg export
                
        Returns:
            True if export successful, False otherwise
        """
        deck_name = kwargs.get('deck_name', settings.anki.deck_name)
        model_name = kwargs.get('model_name', settings.anki.model_name)
        output_path = kwargs.get('output_path')
        
        # If output path provided, export to .apkg file
        if output_path:
            return self.export_to_apkg(notes, output_path, deck_name)
            
        # Otherwise export via AnkiConnect
        try:
            # Create deck if it doesn't exist
            if not await self.create_deck(deck_name):
                return False

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
            logger.error(f"Failed to export notes to Anki: {e}")
            return False

    def export_to_apkg(
        self,
        notes: List[Dict[str, str]],
        output_path: str,
        deck_name: str
    ) -> bool:
        """Export notes to .apkg file
        
        Args:
            notes: List of notes to export
            output_path: Path to save the .apkg file
            deck_name: Name of the deck
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create deck
            deck = genanki.Deck(
                2059400110,  # Random deck ID
                deck_name
            )

            # Add notes to deck
            for note_fields in notes:
                note = genanki.Note(
                    model=self.model,
                    fields=[
                        note_fields.get('Front', ''),
                        note_fields.get('Back', ''),
                        note_fields.get('Phonetic', ''),
                        note_fields.get('Examples', ''),
                        note_fields.get('Collins', '')
                    ]
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