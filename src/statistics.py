"""Funciones de estadistica descriptiva."""

import pandas as pd


def summarize_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Resume columnas numericas usando estadisticas descriptivas."""
    return df.describe().transpose()
