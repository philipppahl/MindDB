import pytest
from datetime import datetime
from sqlite3 import IntegrityError

from minddb.storage import DB


@pytest.fixture
def db():
    db = DB(':memory:')
    db.create_tables()
    yield db
    db.close()


@pytest.fixture
def sample_deck(db):
    """Fixture providing a sample deck."""
    deck_id = db.insert_deck("Test Deck")
    return db.get_deck(deck_id)


def test_insert_note(db, sample_deck):
    """Test inserting a new note."""
    # Given
    note_data = {
        "deck_id": sample_deck.id,
        "question": "What is the capital of France?",
        "answer_a": "London",
        "answer_b": "Paris",
        "answer_c": "Berlin",
        "answer_d": "Madrid",
        "correct_answer": "b",
        "explanation": "Paris is the capital of France"
    }

    # When
    note_id = db.insert_note(**note_data)

    # Then
    assert note_id is not None
    saved_note = db.get_note(note_id)
    assert saved_note.question == note_data["question"]
    assert saved_note.answer_a == note_data["answer_a"]
    assert saved_note.answer_b == note_data["answer_b"]
    assert saved_note.answer_c == note_data["answer_c"]
    assert saved_note.answer_d == note_data["answer_d"]
    assert saved_note.correct_answer == note_data["correct_answer"]
    assert saved_note.explanation == note_data["explanation"]
    assert isinstance(saved_note.created_at, datetime)


def test_get_nonexistent_note(db):
    """Test getting a note that doesn't exist."""
    # When
    note = db.get_note(999)

    # Then
    assert note is None


def test_create_note_invalid_answer(db, sample_deck):
    """Test creating a note with invalid correct_answer."""
    with pytest.raises(IntegrityError):
        # Manually execute SQL to test database constraint
        db.connect().execute(
            """
            INSERT INTO notes (deck_id, question, correct_answer, explanation)
            VALUES (?, ?, ?, ?)
            """,
            (sample_deck.id, "question", "x", "explanation")
        )


def test_insert_note_minimal_fields(db, sample_deck):
    """Test inserting a note with only required fields."""
    # Given
    note_data = {
        "deck_id": sample_deck.id,
        "question": "Test question",
        "explanation": "Test explanation"
    }

    # When
    note_id = db.insert_note(**note_data)

    # Then
    saved_note = db.get_note(note_id)
    assert saved_note.question == note_data["question"]
    assert saved_note.explanation == note_data["explanation"]
    assert saved_note.answer_a is None
    assert saved_note.answer_b is None
    assert saved_note.answer_c is None
    assert saved_note.answer_d is None
    assert saved_note.correct_answer is None


@pytest.fixture
def sample_note(db, sample_deck):
    """Fixture providing a sample note."""
    note_id = db.insert_note(
        deck_id=sample_deck.id,
        question="Test question",
        answer_a="A1",
        answer_b="A2",
        answer_c="A3",
        answer_d="A4",
        correct_answer="a",
        explanation="Test explanation"
    )

    return db.get_note(note_id)


@pytest.fixture
def sample_client_import(db):
    """Fixture providing a sample client import."""
    client_id = "test_client_123"
    import_id = db.create_client_import(client_id)
    return db.get_client_import(import_id)


def test_link_note_to_client_import(db, sample_note, sample_client_import):
    """Test linking a note to a client import."""
    # When
    db.link_note_to_client_import(sample_note.id, sample_client_import.id)

    # Then
    notes = db.get_notes_by_client_import(sample_client_import.id)
    assert len(notes) == 1
    assert notes[0].id == sample_note.id

    imports = db.get_client_imports_by_note(sample_note.id)
    assert len(imports) == 1
    assert imports[0].id == sample_client_import.id


def test_link_note_to_client_import_duplicate(db, sample_note,
                                              sample_client_import):
    """Test linking the same note to a client import multiple times."""
    # Given
    db.link_note_to_client_import(sample_note.id, sample_client_import.id)

    # When/Then
    with pytest.raises(IntegrityError):
        db.link_note_to_client_import(sample_note.id, sample_client_import.id)


def test_link_nonexistent_note(db, sample_client_import):
    """Test linking a nonexistent note."""
    # When/Then
    with pytest.raises(IntegrityError):
        db.link_note_to_client_import(999, sample_client_import.id)


def test_link_nonexistent_client_import(db, sample_note):
    """Test linking to a nonexistent client import."""
    # When/Then
    with pytest.raises(IntegrityError):
        db.link_note_to_client_import(sample_note.id, 999)


def test_get_notes_by_client_import_empty(db, sample_client_import):
    """Test getting notes for a client import with no links."""
    # When
    notes = db.get_notes_by_client_import(sample_client_import.id)

    # Then
    assert len(notes) == 0


def test_get_client_imports_by_note_empty(db, sample_note):
    """Test getting client imports for a note with no links."""
    # When
    imports = db.get_client_imports_by_note(sample_note.id)

    # Then
    assert len(imports) == 0


def test_multiple_notes_per_client_import(db, sample_client_import,
                                          sample_deck):
    """Test linking multiple notes to one client import."""
    # Given
    notes = []
    for i in range(3):
        note_id = db.insert_note(
            deck_id=sample_deck.id,
            question=f"Question {i}",
            explanation=f"Explanation {i}"
        )
        notes.append(db.get_note(note_id))
        db.link_note_to_client_import(note_id, sample_client_import.id)

    # When
    linked_notes = db.get_notes_by_client_import(sample_client_import.id)

    # Then
    assert len(linked_notes) == 3
    assert {n.id for n in linked_notes} == {n.id for n in notes}


def test_multiple_client_imports_per_note(db, sample_note):
    """Test linking multiple client imports to one note."""
    # Given
    imports = []
    for i in range(3):
        import_id = db.create_client_import(f"client_{i}")
        imports.append(db.get_client_import(import_id))
        db.link_note_to_client_import(sample_note.id, import_id)

    # When
    linked_imports = db.get_client_imports_by_note(sample_note.id)

    # Then
    assert len(linked_imports) == 3
    assert {ci.id for ci in linked_imports} == {ci.id for ci in imports}
