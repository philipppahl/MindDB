from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional


class Transcript(BaseModel):
    """Model representing a transcript record.

    A transcript is a processed text file containing the raw content
    to be analyzed and converted into flashcards.
    """
    id: int
    filename: str
    checksum: int
    created_at: datetime


class Deck(BaseModel):
    """Model representing a deck of flashcards.

    A deck is a collection of related flashcards that can be studied together.
    It helps organize cards by topic or learning objective.
    """
    id: int
    name: str
    created_at: datetime


class TranscriptDeckProcessing(BaseModel):
    """Model representing the relationship between transcripts and decks.

    This tracks which transcripts have been processed into which decks,
    allowing for many-to-many relationships between transcripts and decks.
    """
    id: int
    deck_id: int
    transcript_id: int
    created_at: datetime


class Note(BaseModel):
    """Model representing a flashcard note.

    A note contains the question, multiple choice answers, and explanation
    for a single flashcard. It can optionally include up to 4 answer choices
    and indicate which is correct using 'a', 'b', 'c', or 'd'.
    Each note belongs to a specific deck.
    """
    id: int
    deck_id: int
    question: str
    answer_a: Optional[str] = None
    answer_b: Optional[str] = None
    answer_c: Optional[str] = None
    answer_d: Optional[str] = None
    correct_answer: Optional[Literal['a', 'b', 'c', 'd']] = None
    explanation: Optional[str] = None
    created_at: datetime


class ClientImport(BaseModel):
    """Model representing an import from a client application.

    Tracks imports of notes into external client applications, allowing
    the system to maintain records of which notes have been imported by which
    client and when they were imported.
    """
    id: Optional[int] = None
    client_id: str
    created_at: Optional[datetime] = None
