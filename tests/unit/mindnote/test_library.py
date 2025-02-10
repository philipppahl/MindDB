import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from minddb.mindnote.library import Library


@pytest.fixture
def mock_catalog():
    catalog = Mock()
    # Setup default mock deck
    mock_deck = Mock()
    mock_deck.id = 1
    mock_deck.name = "Test Deck"
    catalog.get_or_create_deck.return_value = mock_deck
    return catalog


@pytest.fixture
def library():
    return Library(path="dummy/path")


def test_library_init():
    """Test Library initialization."""
    # Given
    path = "test/path"

    # When
    library = Library(path)

    # Then
    assert library._path == Path(path).resolve()
    assert library._unlinked_transcripts == []
    assert library._mime_types == ['.txt', '.md']


def test_get_files_raises_when_path_not_found(library):
    """Test _get_files raises FileNotFoundError for non-existent path."""
    with pytest.raises(FileNotFoundError):
        library._get_files("Test Deck")


@patch('pathlib.Path.exists')
@patch('pathlib.Path.iterdir')
def test_get_files_raises_when_no_valid_files(mock_iterdir, mock_exists,
                                              library):
    """Test _get_files raises ValueError when no valid files found."""
    # Given
    mock_exists.return_value = True
    mock_iterdir.return_value = [
        Path('test.pdf'),
        Path('test.doc')
    ]

    # When/Then
    with pytest.raises(ValueError):
        library._get_files("Test Deck")


@patch('pathlib.Path.exists')
@patch('pathlib.Path.iterdir')
@patch('minddb.storage.get_catalog')
@patch('minddb.tools.get_checksum')
def test_get_files_returns_unprocessed_files(mock_checksum, mock_get_catalog,
                                             mock_iterdir, mock_exists,
                                             library, mock_catalog):
    """Test _get_files returns only unprocessed files."""
    # Given
    mock_exists.return_value = True
    mock_files = [Path('test1.txt'), Path('test2.txt'), Path('test3.md')]
    mock_iterdir.return_value = mock_files
    mock_get_catalog.return_value = mock_catalog
    mock_checksum.return_value = "abc123"

    # Mock catalog to say only first file is processed
    mock_catalog.is_file_processed.side_effect = [True, False, False]

    # When
    result = library._get_files("Test Deck")

    # Then
    assert len(result) == 2
    assert Path('test2.txt') in result
    assert Path('test3.md') in result
    assert len(library._unlinked_transcripts) == 2


def test_link_transcripts(library, mock_catalog):
    """Test link_transcripts properly links transcripts to deck."""
    # Given
    library._unlinked_transcripts = [
        {'filename': 'test1.txt', 'checksum': 'abc123', 'deck_id': 1},
        {'filename': 'test2.txt', 'checksum': 'def456', 'deck_id': 1}
    ]
    mock_catalog.get_or_insert_transcript.return_value = 99

    with patch('minddb.storage.get_catalog', return_value=mock_catalog):
        # When
        library.link_transcripts()

        # Then
        assert mock_catalog.get_or_insert_transcript.call_count == 2
        assert mock_catalog.link_transcript_to_deck.call_count == 2
        assert library._unlinked_transcripts == []


@patch('pathlib.Path.exists')
@patch('pathlib.Path.iterdir')
@patch('minddb.storage.get_catalog')
@patch('minddb.tools.get_checksum')
def test_get_transcript_returns_none_when_no_unprocessed_content(
        mock_checksum, mock_get_catalog, mock_iterdir, mock_exists,
        library, mock_catalog):
    """Test get_transcript returns None when no unprocessed content
    available."""
    # Given
    mock_exists.return_value = True
    mock_files = [Path('test1.txt')]
    mock_iterdir.return_value = mock_files
    mock_get_catalog.return_value = mock_catalog
    mock_checksum.return_value = "abc123"
    mock_catalog.is_file_processed.return_value = True

    # When
    result = library.get_transcript("Test Deck")

    # Then
    assert result is None


@patch('pathlib.Path.exists')
@patch('pathlib.Path.iterdir')
@patch('minddb.storage.get_catalog')
@patch('minddb.tools.get_checksum')
def test_get_transcript_returns_combined_content(
        mock_checksum, mock_get_catalog, mock_iterdir, mock_exists,
        library, mock_catalog):
    """Test get_transcript returns combined content from unprocessed files."""
    # Given
    mock_exists.return_value = True
    mock_files = [Path('test1.txt'), Path('test2.txt')]
    mock_iterdir.return_value = mock_files
    mock_get_catalog.return_value = mock_catalog
    mock_checksum.return_value = "abc123"
    mock_catalog.is_file_processed.return_value = False

    # Mock file reading
    mock_content = {
        'test1.txt': 'Content 1',
        'test2.txt': 'Content 2'
    }

    with patch('builtins.open', mock_open()) as mock_file:
        def mock_read():
            filename = mock_file.call_args[0][0].name
            return mock_content[filename]

        mock_reader = mock_file.return_value.__enter__.return_value
        mock_reader.read.side_effect = mock_read

        # When
        result = library.get_transcript("Test Deck")

        # Then
        assert "# test1.txt" in result
        assert "Content 1" in result
        assert "# test2.txt" in result
        assert "Content 2" in result
