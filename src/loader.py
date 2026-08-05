"""Funciones para descubrir y cargar datos del proyecto."""

from pathlib import Path

import pandas as pd

from src.config import RAW_DATA_DIR


def list_csv_files() -> list[Path]:
    """
    Return all CSV files located in the raw data directory.

    Returns
    -------
    list[Path]
        List of CSV file paths.

    Raises
    ------
    FileNotFoundError
        If the raw data directory does not exist.
    """

    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(f"Raw data directory not found: {RAW_DATA_DIR}")

    return sorted(RAW_DATA_DIR.glob("*.csv"))


def load_dataset(file_path: Path) -> pd.DataFrame:
    """
    Load a CSV dataset.

    Parameters
    ----------
    file_path : Path
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        Loaded dataset.
    """

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    return pd.read_csv(file_path)
