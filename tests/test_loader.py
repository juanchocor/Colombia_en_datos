from pathlib import Path

import pandas as pd
import pytest

from src.loader import list_csv_files, load_dataset


def test_list_csv_files_returns_paths():
    """The loader should return a list of Path objects."""

    files = list_csv_files()

    assert isinstance(files, list)
    assert all(isinstance(file, Path) for file in files)


def test_all_files_are_csv():
    """Every discovered file must have the .csv extension."""

    files = list_csv_files()

    assert all(file.suffix == ".csv" for file in files)


def test_raw_directory_is_not_empty():
    """The raw directory should contain at least one CSV file."""

    files = list_csv_files()

    assert len(files) > 0


def test_load_dataset_returns_dataframe():
    """Loading a discovered dataset should return a DataFrame."""

    files = list_csv_files()
    df = load_dataset(files[0])

    assert isinstance(df, pd.DataFrame)


def test_loaded_dataframe_is_not_empty():
    """A discovered dataset should load with at least one row."""

    files = list_csv_files()
    df = load_dataset(files[0])

    assert not df.empty


def test_loading_missing_file_raises_error():
    """Loading a missing file should raise FileNotFoundError."""

    with pytest.raises(FileNotFoundError):
        load_dataset(Path("missing.csv"))
