import pytest
from pathlib import Path
import zlib
from minddb.tools import get_checksum


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file with test content."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    return file_path


@pytest.fixture
def empty_file(tmp_path):
    """Create an empty temporary file."""
    file_path = tmp_path / "empty.txt"
    file_path.write_text("")
    return file_path


def test_get_checksum_with_file(temp_file):
    """Test checksum generation with a file containing text."""
    # When
    checksum = get_checksum(temp_file)

    # Then
    assert isinstance(checksum, int)  # adler32 returns an integer
    # Verify against known adler32 value for "test content"
    assert checksum == zlib.adler32(b"test content")


def test_get_checksum_with_empty_file(empty_file):
    """Test checksum generation with an empty file."""
    # When
    checksum = get_checksum(empty_file)

    # Then
    assert checksum == zlib.adler32(b"")  # adler32 of empty content


def test_get_checksum_with_unicode_content(tmp_path):
    """Test checksum generation with unicode characters in file."""
    # Given
    content = "Unicode test: 你好世界"
    file_path = tmp_path / "unicode.txt"
    file_path.write_text(content)

    # When
    checksum = get_checksum(file_path)

    # Then
    assert isinstance(checksum, int)
    assert checksum == zlib.adler32(content.encode('utf-8'))


def test_get_checksum_file_not_found():
    """Test that non-existent file raises FileNotFoundError."""
    # Given
    non_existent_file = Path("does_not_exist.txt")

    # When/Then
    with pytest.raises(FileNotFoundError):
        get_checksum(non_existent_file)


def test_get_checksum_with_directory(tmp_path):
    """Test that directory input raises IsADirectoryError."""
    # When/Then
    with pytest.raises(IsADirectoryError):
        get_checksum(tmp_path)


def test_get_checksum_with_different_path_types(temp_file):
    """Test that different path types produce same checksum."""
    # Given
    str_path = str(temp_file)
    path_obj = Path(temp_file)

    # When
    checksum1 = get_checksum(str_path)
    checksum2 = get_checksum(path_obj)

    # Then
    assert checksum1 == checksum2


def test_get_checksum_binary_file(tmp_path):
    """Test checksum generation with binary content."""
    # Given
    binary_content = bytes([0x00, 0xFF, 0x10, 0x20, 0x30])
    file_path = tmp_path / "binary.bin"
    file_path.write_bytes(binary_content)

    # When
    checksum = get_checksum(file_path)

    # Then
    assert isinstance(checksum, int)
    assert checksum == zlib.adler32(binary_content)
