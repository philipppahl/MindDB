from .db import DB
from .db_storage import DBStorage
from .models import Transcript

# Global catalog instance
_catalog = None

__all__ = ['DB', 'Transcript', 'setup', 'get_catalog']


def setup(path, name):
    """Configure the global catalog database.

    Args:
        path: Directory path where catalog is stored
        name: Name of the catalog database
    """
    global _catalog
    _catalog = DBStorage(path, name)
    return _catalog


def get_catalog():
    """Get the configured catalog database.

    Returns:
        DBStorage: The configured catalog instance

    Raises:
        RuntimeError: If catalog is not configured
    """
    if _catalog is None:
        msg = "Catalog not configured. Call configure_catalog first."
        raise RuntimeError(msg)

    return _catalog


def close_catalog():
    """Close the global catalog database connection.

    This should be called when the application is shutting down
    to ensure proper cleanup of database resources.
    """
    global _catalog
    if _catalog is not None:
        _catalog.close()
        _catalog = None
