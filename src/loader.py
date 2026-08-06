from pathlib import Path

import pandas as pd

from src.config import DEFAULT_ENCODING


def load_csv(path: str | Path, encoding: str = DEFAULT_ENCODING) -> pd.DataFrame:
    """Carga un archivo CSV y devuelve un DataFrame."""
    return pd.read_csv(path, encoding=encoding)


def load_raw_data(data_dir: str | Path) -> dict[str, pd.DataFrame]:
    """
    Carga todos los CSV de un directorio y los devuelve
    como un diccionario de DataFrames.
    """

    data_dir = Path(data_dir)

    datasets = {}

    for file in sorted(data_dir.glob("*.csv")):
        datasets[file.stem] = load_csv(file)

    return datasets