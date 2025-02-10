import logging
from pathlib import Path

import minddb.tools

logger = logging.getLogger(__name__)


class Library:
    def __init__(self, path):
        """
        Initialize a Library object.

        Args:
            path: Path to the library directory, holding the transcripts, etc.
                 Can be absolute or relative path.
        """
        self._path = Path(path).resolve()  # Convert to absolute path
        self._unlinked_transcripts = []
        self._mime_types = ['.txt', '.md']

    def _get_files(self, deck_name):
        """Get all valid files from the library directory.

        Returns:
            list: List of Path objects for valid files

        Raises:
            ValueError: If no valid files found
            FileNotFoundError: If library directory doesn't exist
        """
        if not self._path.exists():
            raise FileNotFoundError(f"Library path not found: {self._path}")

        files = [
            f for f in self._path.iterdir() if f.suffix in self._mime_types
        ]
        files.sort()

        if not files:
            msg = f"No {self._mime_types} files found in {self._path}"
            raise ValueError(msg)

        catalog = minddb.storage.get_catalog()

        logger.debug(f"Found {len(files)} files in {self._path}")
        logger.debug(f"Deck: {deck_name}")

        unprocessed_files = []
        self._unlinked_transcripts = []
        deck = catalog.get_or_create_deck(name=deck_name)
        for file in files:
            checksum = minddb.tools.get_checksum(file)
            logger.debug(f"File {file.name} checksum: {checksum}")
            if not catalog.is_file_processed(file.name, checksum, deck.name):
                self._unlinked_transcripts.append({
                    'filename': file.name,
                    'checksum': checksum,
                    'deck_id': deck.id,
                })
                unprocessed_files.append(file)

        return unprocessed_files

    def link_transcripts(self):
        """Link processed transcripts to the deck."""
        catalog = minddb.storage.get_catalog()
        for file in self._unlinked_transcripts:
            transcript_id = catalog.get_or_insert_transcript(**file)
            catalog.link_transcript_to_deck(file['deck_id'], transcript_id)

        self._unlinked_transcripts = []

    def get_transcript(self, deck):
        """
        Get the transcripts for a given deck. Only add unprocessed content.

        Args:
            deck: Name of the deck

        Returns:
            str: Transcript for the deck


        Raises:
            ValueError: If no valid files found or no unprocessed content
                        was available
        """

        transcript = []

        for file_path in self._get_files(deck):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:  # Only add non-empty content
                    transcript.append(f"# {file_path.name}\n\n{content}")

        if not transcript:
            logger.warning(f"No unprocessed content found for deck: {deck}")
            return None

        return "\n\n".join(transcript)
