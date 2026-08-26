from src.config import RAW_DATA_DIR


def test_raw_directory_exists():
    """The raw data directory must exist."""
    assert RAW_DATA_DIR.exists()
    assert RAW_DATA_DIR.is_dir()