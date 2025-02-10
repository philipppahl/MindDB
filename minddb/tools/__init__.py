import zlib
from pathlib import Path


def get_checksum(path):
    """Get checksum of file using the adler-32 algorithm.
    Args:
        path: Path to the file (str or Path object)

    Returns:
        int: Checksum of the file

    Raises:
        FileNotFoundError: If the file does not exist
        IsADirectoryError: If the path points to a directory
        TypeError: If path is not str or Path
    """
    # Convert string path to Path object if needed
    if isinstance(path, str):
        path = Path(path)
    elif not isinstance(path, Path):
        raise TypeError("Path must be string or Path object")

    # Check if path exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Check if path is a directory
    if path.is_dir():
        raise IsADirectoryError(f"Path is a directory: {path}")

    # Read file and calculate checksum
    with open(path, 'rb') as f:
        return zlib.adler32(f.read())
    return zlib.adler32(f.read())
