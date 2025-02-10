import pytest
import sqlite3
from datetime import datetime
from minddb.storage.db import DB
from minddb.storage.models import Deck, Transcript


@pytest.fixture
def db():
    db = DB(':memory:')
    db.create_tables()
    yield db
    db.close()


@pytest.fixture
def sample_deck(db):
    """Create a sample deck for testing."""
    deck_id = db.insert_deck("Test Deck")
    return db.get_deck(deck_id)


@pytest.fixture
def sample_transcript(db):
    """Create a sample transcript for testing."""
    transcript_id = db.insert_transcript("test.txt", 12345)
    return db.get_transcript(transcript_id)


def test_insert_deck(db):
    """Test creating a new deck."""
    # When
    deck_id = db.insert_deck("Test Deck")
    deck = db.get_deck(deck_id)

    # Then
    assert isinstance(deck, Deck)
    assert deck.id == deck_id
    assert deck.name == "Test Deck"
    assert isinstance(deck.created_at, datetime)


def test_get_deck_not_found(db):
    """Test getting a non-existent deck."""
    # When
    deck = db.get_deck(999)

    # Then
    assert deck is None


def test_get_all_decks(db):
    """Test retrieving all decks."""
    # Given
    deck_names = ["Deck 1", "Deck 2", "Deck 3"]
    for name in deck_names:
        db.insert_deck(name)

    # When
    decks = db.get_all_decks()

    # Then
    assert len(decks) == 3
    assert all(isinstance(deck, Deck) for deck in decks)
    assert {deck.name for deck in decks} == set(deck_names)


def test_link_transcript_to_deck(db, sample_deck, sample_transcript):
    """Test linking a transcript to a deck."""
    # When
    link_id = db.link_transcript_to_deck(sample_deck.id, sample_transcript.id)

    # Then
    assert link_id > 0
    deck_transcripts = db.get_deck_transcripts(sample_deck.id)
    assert len(deck_transcripts) == 1
    assert deck_transcripts[0].filename == sample_transcript.filename
    assert deck_transcripts[0].checksum == sample_transcript.checksum


def test_get_deck_transcripts_empty(db, sample_deck):
    """Test getting transcripts for a deck with no transcripts."""
    # When
    transcripts = db.get_deck_transcripts(sample_deck.id)

    # Then
    assert isinstance(transcripts, list)
    assert len(transcripts) == 0


def test_get_deck_transcripts_multiple(db, sample_deck):
    """Test getting multiple transcripts for a deck."""
    # Given
    files = [
        ("file1.txt", 11111),
        ("file2.txt", 22222),
        ("file3.txt", 33333)
    ]

    for filename, checksum in files:
        transcript_id = db.insert_transcript(filename, checksum)
        db.link_transcript_to_deck(sample_deck.id, transcript_id)

    # When
    transcripts = db.get_deck_transcripts(sample_deck.id)

    # Then
    assert len(transcripts) == 3
    assert all(isinstance(t, Transcript) for t in transcripts)
    assert {t.filename for t in transcripts} == {td[0] for td in files}
    assert {t.checksum for t in transcripts} == {td[1] for td in files}


def test_link_transcript_to_deck_invalid_deck(db, sample_transcript):
    """Test linking a transcript to a non-existent deck."""
    # When/Then
    with pytest.raises(sqlite3.IntegrityError):
        db.link_transcript_to_deck(999, sample_transcript.id)


def test_link_transcript_to_deck_invalid_transcript(db, sample_deck):
    """Test linking a non-existent transcript to a deck."""
    # When/Then
    with pytest.raises(sqlite3.IntegrityError):
        db.link_transcript_to_deck(sample_deck.id, 999)


def test_link_transcript_to_deck_duplicate(db, sample_deck, sample_transcript):
    """Test linking the same transcript to a deck multiple times."""
    # Given
    db.link_transcript_to_deck(sample_deck.id, sample_transcript.id)
    """Test linking the same transcript to a deck multiple times."""
    # When/Then
    with pytest.raises(sqlite3.IntegrityError):
        db.link_transcript_to_deck(sample_deck.id, sample_transcript.id)
        db.link_transcript_to_deck(sample_deck.id, sample_transcript.id)
