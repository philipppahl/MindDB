import pytest
from minddb.storage import setup, get_catalog


@pytest.fixture
def reset_catalog():
    """Reset the catalog before and after each test."""
    import minddb.storage
    minddb.storage._catalog = None
    yield
    minddb.storage._catalog = None


def test_setup(tmp_path, reset_catalog):
    """Test that setup creates a DBStorage instance."""
    # When
    catalog = setup(str(tmp_path), "test_catalog")

    # Then
    assert catalog.path == str(tmp_path)
    assert catalog.name == "test_catalog"
    assert catalog.db_path.endswith("test_catalog.db")


def test_get_catalog_returns_configured_instance(tmp_path, reset_catalog):
    """Test that get_catalog returns the configured catalog instance."""
    # Given
    configured = setup(str(tmp_path), "test_catalog")

    # When
    retrieved = get_catalog()

    # Then
    assert retrieved is configured  # Same instance
    assert retrieved.path == str(tmp_path)
    assert retrieved.name == "test_catalog"


def test_get_catalog_without_configuration(reset_catalog):
    """Test that get_catalog raises error when not configured."""
    # When/Then
    with pytest.raises(RuntimeError) as exc_info:
        get_catalog()
    assert "Catalog not configured" in str(exc_info.value)


def test_resetup(tmp_path, reset_catalog):
    """Test that catalog can be reconfigured."""
    # Given
    setup(str(tmp_path), "first_catalog")

    # When
    second = setup(str(tmp_path), "second_catalog")

    # Then
    assert get_catalog() is second
    assert get_catalog().name == "second_catalog"


def test_catalog_is_singleton(tmp_path, reset_catalog):
    """Test that catalog maintains singleton pattern."""
    # Given
    setup(str(tmp_path), "test_catalog")

    # When
    catalog1 = get_catalog()
    catalog2 = get_catalog()

    # Then
    assert catalog1 is catalog2  # Same instance


def test_setup_with_different_paths(tmp_path, reset_catalog):
    """Test setup with different path types."""
    # Given
    path_str = str(tmp_path)

    # When
    catalog = setup(path_str, "test_catalog")

    # Then
    assert catalog.path == path_str
