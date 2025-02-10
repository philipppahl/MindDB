import logging
import instructor
import anthropic
from pydantic import BaseModel
from typing import List, Literal, Optional

import minddb.mindnote.prompts

logger = logging.getLogger(__name__)


class Note(BaseModel):
    """Model representing a flashcard note.

    A note contains the question, multiple choice answers, and explanation
    for a single flashcard. It can optionally include up to 4 answer choices
    and indicate which is correct using 'a', 'b', 'c', or 'd'.
    """
    id: int
    question: str
    answer_a: Optional[str] = None
    answer_b: Optional[str] = None
    answer_c: Optional[str] = None
    answer_d: Optional[str] = None
    correct_answer: Optional[Literal['a', 'b', 'c', 'd']] = None
    explanation: Optional[str] = None


class Notes(BaseModel):
    """Collection of flashcard notes"""
    notes: List[Note]


class Processor:
    def __init__(self, library_path):
        self._library = minddb.mindnote.Library(path=library_path)
        self._notes = []
        self._client = instructor.from_anthropic(anthropic.Anthropic())

    def create(self, deck_name):
        logger.info(f"Creating notes for deck: {deck_name}. Bear with me...")
        transcript = self._library.get_transcript(deck_name)

        if transcript is None:
            return

        notes = self._client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": minddb.mindnote.prompts.transcript_to_notes
            }],
            response_model=Notes,
            context={'transcript': self._library.get_transcript(deck_name)},
            max_retries=2
        )

        logger.info(f"Created {len(notes.notes)} notes for deck: {deck_name}")

        catalog = minddb.storage.get_catalog()
        deck = catalog.get_or_create_deck(name=deck_name)
        for note in notes.notes:
            logger.debug(f"Inserting note: {note}")
            catalog.insert_note(**note.dict(), deck_id=deck.id)

        self._library.link_transcripts()
