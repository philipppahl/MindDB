import pytest
from contextlib import closing
from minddb.storage.models import Transcript
from minddb.storage import DB


@pytest.fixture
def db():
    db = DB(':memory:')
    db.create_tables()
    yield db
    db.close()


class TestDB:
    def test_table_creation(self, db):
        """Test that database tables are created correctly."""
        tables = db.list_tables()
        assert 'transcripts' in tables

    def test_insert_transcript(self, db):
        """Test inserting a single transcript."""
        record_id = db.insert_transcript("test.txt", 12345)
        assert record_id > 0

        transcripts = db.get_transcripts("test.txt")
        assert len(transcripts) == 1
        assert transcripts[0].filename == "test.txt"
        assert transcripts[0].checksum == 12345

    def test_insert_multiple_transcripts_same_filename(self, db):
        """Test inserting multiple transcripts with the same filename."""
        id1 = db.insert_transcript("test.txt", 12345)
        id2 = db.insert_transcript("test.txt", 67890)

        assert id1 != id2

        transcripts = db.get_transcripts("test.txt")
        assert len(transcripts) == 2
        checksums = {t.checksum for t in transcripts}
        assert checksums == {12345, 67890}

    def test_get_nonexistent_transcript(self, db):
        """Test retrieving a transcript that doesn't exist."""
        transcripts = db.get_transcripts("nonexistent.txt")
        assert len(transcripts) == 0

    def test_delete_transcripts(self, db):
        """Test deleting all transcripts for a filename."""
        # Insert multiple transcripts
        db.insert_transcript("test.txt", 12345)
        db.insert_transcript("test.txt", 67890)

        # Delete all transcripts for this filename
        deleted_count = db.delete_transcripts("test.txt")
        assert deleted_count == 2

        # Verify transcripts were deleted
        remaining = db.get_transcripts("test.txt")
        assert len(remaining) == 0

    def test_delete_nonexistent_transcript(self, db):
        """Test deleting a transcript that doesn't exist."""
        deleted_count = db.delete_transcripts("nonexistent.txt")
        assert deleted_count == 0

    def test_database_connection_management(self, db):
        """Test database connection management."""
        # Test that connection is established
        assert db._connection is not None

        # Test that connection remains the same
        conn1 = db.connect()
        conn2 = db.connect()
        assert conn1 is conn2

        # Test connection close
        db.close()
        assert db._connection is None

    @pytest.mark.parametrize("filename,checksum", [
        ("test1.txt", 11111),
        ("test2.txt", 22222),
        ("test3.txt", 33333),
    ])
    def test_multiple_transcripts(self, db, filename, checksum):
        """Test handling multiple different transcripts."""
        record_id = db.insert_transcript(filename, checksum)
        assert record_id > 0

        transcripts = db.get_transcripts(filename)
        assert len(transcripts) == 1
        assert transcripts[0].filename == filename
        assert transcripts[0].checksum == checksum

    def test_timestamp_creation(self, db):
        """Test that timestamps are automatically set on record creation."""
        db.insert_transcript("test.txt", 12345)
        transcripts = db.get_transcripts("test.txt")

        assert len(transcripts) == 1
        transcript = transcripts[0]
        assert isinstance(transcript, Transcript)
        assert transcript.created_at is not None

        # Insert another record and verify different timestamp
        db.insert_transcript("test.txt", 67890)
        transcripts = db.get_transcripts("test.txt")

        assert len(transcripts) == 2
        assert transcripts[0].created_at >= transcripts[1].created_at

        # Verify model validation
        for t in transcripts:
            assert isinstance(t, Transcript)
            t_dict = t.model_dump()
            cols = ['filename', 'checksum', 'created_at']
            assert all(k in t_dict for k in cols)

    def test_is_file_processed_returns_false_for_new_file(self, db):
        """Test that is_file_processed returns False for unprocessed file."""
        # Given
        deck_name = "test_deck"
        db.insert_deck(deck_name)

        # When
        result = db.is_file_processed("test.txt", 123456, deck_name)

        # Then
        assert result is False

    def test_is_file_processed_returns_true_for_processed_file(self, db):
        """Test that is_file_processed returns True for processed file."""
        # Given
        deck_name = "test_deck"
        deck_id = db.insert_deck(deck_name)
        transcript_id = db.insert_transcript("test.txt", 123456)
        db.link_transcript_to_deck(deck_id, transcript_id)

        # When
        result = db.is_file_processed("test.txt", 123456, deck_name)

        # Then
        assert result is True

    def test_is_file_processed_returns_false_for_different_checksum(self, db):
        """Test that is_file_processed returns False when checksum differs."""
        # Given
        deck_name = "test_deck"
        deck_id = db.insert_deck(deck_name)
        transcript_id = db.insert_transcript("test.txt", 123456)
        db.link_transcript_to_deck(deck_id, transcript_id)

        # When checking with different checksum
        result = db.is_file_processed("test.txt", 789012, deck_name)

        # Then
        assert result is False

    def test_is_file_processed_returns_false_for_nonexistent_deck(self, db):
        """Test that is_file_processed returns False for nonexistent deck."""
        # When
        result = db.is_file_processed("test.txt", 123456, "nonexistent_deck")

        # Then
        assert result is False

    def test_get_or_create_deck_creates_new_deck(self, db):
        """Test that get_or_create_deck creates a new deck when it doesn't
        exist."""
        # Given
        deck_name = "test_deck"

        # When
        deck = db.get_or_create_deck(deck_name)

        # Then
        assert deck is not None
        assert deck.name == deck_name
        assert deck.id is not None
        assert deck.created_at is not None

        # Verify deck was actually created in database
        all_decks = db.get_all_decks()
        assert len(all_decks) == 1
        assert all_decks[0].id == deck.id
        assert all_decks[0].name == deck_name

    def test_get_or_create_deck_returns_existing_deck(self, db):
        """Test that get_or_create_deck returns existing deck when it
        exists."""
        # Given
        deck_name = "test_deck"
        first_deck = db.get_or_create_deck(deck_name)

        # When
        second_deck = db.get_or_create_deck(deck_name)

        # Then
        assert second_deck is not None
        assert second_deck.id == first_deck.id
        assert second_deck.name == deck_name
        assert second_deck.created_at == first_deck.created_at

        # Verify only one deck exists in database
        all_decks = db.get_all_decks()
        assert len(all_decks) == 1

    def test_get_or_create_deck_with_different_names(self, db):
        """Test that get_or_create_deck creates separate decks for different
        names."""
        # Given
        deck1_name = "deck1"
        deck2_name = "deck2"

        # When
        deck1 = db.get_or_create_deck(deck1_name)
        deck2 = db.get_or_create_deck(deck2_name)

        # Then
        assert deck1.id != deck2.id
        assert deck1.name == deck1_name
        assert deck2.name == deck2_name

        # Verify both decks exist in database
        all_decks = db.get_all_decks()
        assert len(all_decks) == 2
        deck_names = {d.name for d in all_decks}
        assert deck_names == {deck1_name, deck2_name}

    def test_list_decks_returns_empty_list_when_no_decks(self, db):
        """Test that list_decks returns an empty list when no decks exist."""
        assert db.list_decks() == []

    def test_get_notes_by_deck_id_returns_empty_list_when_no_notes(self, db):
        """Test that get_notes_by_deck_id returns empty list when deck has no
        notes."""
        # Given
        deck_id = db.insert_deck("Test Deck")

        # When
        notes = db.get_notes_by_deck_id(deck_id)

        # Then
        assert notes == []

    def test_get_notes_by_deck_id_returns_only_notes_for_specified_deck(self,
                                                                        db):
        """Test that get_notes_by_deck_id only returns notes for the specified
        deck."""
        # Given
        deck1_id = db.insert_deck("Deck 1")
        deck2_id = db.insert_deck("Deck 2")

        # Create notes in both decks
        db.insert_note(deck1_id, "Q1 Deck1", "E1")
        db.insert_note(deck1_id, "Q2 Deck1", "E2")
        db.insert_note(deck2_id, "Q1 Deck2", "E3")

        # When
        deck1_notes = db.get_notes_by_deck_id(deck1_id)
        deck2_notes = db.get_notes_by_deck_id(deck2_id)

        # Then
        assert len(deck1_notes) == 2
        assert len(deck2_notes) == 1
        assert all(note.deck_id == deck1_id for note in deck1_notes)
        assert all(note.deck_id == deck2_id for note in deck2_notes)

    def test_delete_deck_and_notes(self, db):
        """Test deleting a deck and all its associated data."""
        # Create test data
        deck_id = db.insert_deck("Test Deck")

        # Add a note to the deck
        note_id = db.insert_note(
            deck_id=deck_id,
            question="Test question",
            explanation="Test explanation"
        )

        # Create a transcript and link it to the deck
        transcript_id = db.insert_transcript("test.txt", 12345)
        db.link_transcript_to_deck(deck_id, transcript_id)

        # Create a client import and link it to the note
        client_import_id = db.create_client_import("test_client")
        db.link_note_to_client_import(note_id, client_import_id)

        # Delete the deck
        result = db.delete_deck_and_notes(deck_id)
        assert result is True

        # Verify deck is deleted
        assert db.get_deck(deck_id) is None

        # Verify notes are deleted
        assert db.get_note(note_id) is None

        # Verify transcript processing link is deleted
        with closing(db.connect().cursor()) as cursor:
            cursor.execute(
                "SELECT 1 FROM transcript_deck_processing WHERE deck_id = ?",
                (deck_id,)
            )
            assert cursor.fetchone() is None

        # Verify note-client import link is deleted
        with closing(db.connect().cursor()) as cursor:
            cursor.execute(
                "SELECT 1 FROM note_client_imports WHERE note_id = ?",
                (note_id,)
            )
            assert cursor.fetchone() is None
