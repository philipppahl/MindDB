from .db import DB

import os
import logging

logger = logging.getLogger(__name__)


class DBStorage(DB):
    """Physical storage handler for database with path management."""
    def __init__(self, path, name):
        """Initialize database storage.

        Args:
            path: Directory path where database is stored
            name: Name of the database file (without extension)
        """
        self.path = path
        self.name = name
        db_file = os.path.join(path, f"{name}.db")

        # Create the path if it doesn't exist and log a message
        self.ensure_path()

        super().__init__(db_file)
        logger.debug("Initialized DBStorage at path: %s with name: %s", path,
                     name)

    @property
    def db_path(self):
        """Get the full database file path.

        Returns:
            str: Full path to the database file
        """
        return self._db_name

    @property
    def exists(self):
        """Check if the database file exists.

        Returns:
            bool: True if database file exists, False otherwise
        """
        return os.path.exists(self._db_name)

    def ensure_path(self):
        """Ensure the database directory exists.

        Creates the directory path if it doesn't exist.
        """
        os.makedirs(self.path, exist_ok=True)
        logger.debug("Ensured database path exists: %s", self.path)
