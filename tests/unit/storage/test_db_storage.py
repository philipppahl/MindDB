import pytest
import os
from minddb.storage.db_storage import DBStorage


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database storage instance."""
    db_path = tmp_path / "databases"
    db = DBStorage(str(db_path), "testdb")
    yield db
    db.close()


def test_db_storage_initialization(temp_db):
    """Test that DBStorage initializes with correct path and name."""
    assert temp_db.name == "testdb"
    assert temp_db.path.endswith("databases")
    assert temp_db.db_path.endswith("testdb.db")


def test_db_storage_creates_directory(tmp_path):
    """Test that DBStorage creates the directory if it doesn't exist."""
    # Given
    db_path = tmp_path / "new_dir" / "subdir"

    # When
    DBStorage(str(db_path), "testdb")

    # Then
    assert os.path.exists(db_path)


def test_db_storage_exists_property(temp_db):
    """Test the exists property returns correct state."""
    assert temp_db.exists


def test_db_storage_path_with_special_chars(tmp_path):
    """Test that DBStorage handles paths with special characters."""
    # Given
    db_path = tmp_path / "test dir with spaces"

    # When
    db = DBStorage(str(db_path), "test-db")

    # Then
    assert os.path.exists(db_path)
    assert db.db_path.endswith("test-db.db")


def test_db_storage_ensure_path_idempotent(tmp_path):
    """Test that calling ensure_path multiple times is safe."""
    # Given
    db_path = tmp_path / "test_db"
    db = DBStorage(str(db_path), "testdb")

    # When
    db.ensure_path()  # Called once in __init__ and again here
    db.ensure_path()  # Third time

    # Then
    assert os.path.exists(db_path)


def test_db_storage_with_absolute_path(tmp_path):
    """Test that DBStorage works with absolute paths."""
    # Given
    abs_path = os.path.abspath(str(tmp_path / "abs_path"))

    # When
    db = DBStorage(abs_path, "testdb")

    # Then
    assert os.path.isabs(db.path)
    assert os.path.exists(abs_path)


def test_db_storage_db_path_property(temp_db):
    """Test that db_path property returns correct full path."""
    # Given/When
    expected_path = os.path.join(temp_db.path, "testdb.db")

    # Then
    assert temp_db.db_path == expected_path


def test_db_storage_inherits_db_functionality(temp_db):
    """Test that DBStorage inherits and can use DB functionality."""
    # When
    temp_db.create_tables()

    # Then
    # Should be able to use inherited DB methods
    # check that tables is not empty
    assert temp_db.list_tables()
