import logging

import minddb.mindnote.prompts
from .notes import get_notes

logger = logging.getLogger(__name__)


class Processor:
    def __init__(self, library_path):
        self._library = minddb.mindnote.Library(path=library_path)

    async def create(self, deck_name):
        """Create the notes

        Steps
        -----
        - Extract key topics
        - Create notes
        """

        logger.info(f"Creating notes for deck: {deck_name}. Bear with me...")
        transcript = self._library.get_transcript(deck_name)

        if transcript is None:
            return

        notes = await get_notes(transcript)

        logger.info((f"Created {len(notes)} notes for deck: "
                     f"{deck_name}"))

        catalog = minddb.storage.get_catalog()
        deck = catalog.get_or_create_deck(name=deck_name)
        logger.debug(f"Deck ID: {deck.id}, deck name: {deck.name}")

        for note in notes:
            note_dict = note.to_dict()

            # Convert Markdown bold to HTML bold in explanation
            if 'explanation' in note_dict and note_dict['explanation']:
                import re
                # Find all occurrences of **word** and replace with <b>word</b>
                note_dict['explanation'] = re.sub(
                    r'\*\*([^*]+)\*\*',
                    r'<b>\1</b>',
                    note_dict['explanation']
                )

            catalog.insert_note(**note_dict, deck_id=deck.id)

        self._library.link_transcripts()
