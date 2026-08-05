"""Funciones genericas de limpieza para DataFrames."""

from __future__ import annotations

import pandas as pd

from src.utils import normalize_column_name


def drop_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas completamente vacias."""
    return df.dropna(how="all").copy()


def drop_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas duplicadas exactas."""
    return df.drop_duplicates().copy()


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Estandariza nombres de columnas a un formato uniforme."""
    cleaned = df.copy()
    cleaned.columns = [normalize_column_name(str(column)) for column in cleaned.columns]
    return cleaned


def trim_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica trim a todas las columnas de texto."""
    cleaned = df.copy()
    string_columns = cleaned.select_dtypes(include=["object", "string"]).columns
    for column in string_columns:
        cleaned[column] = cleaned[column].apply(
            lambda value: value.strip() if isinstance(value, str) else value
        )
    return cleaned


def convert_numeric_columns(
    df: pd.DataFrame, numeric_columns: list[str]
) -> pd.DataFrame:
    """Convierte columnas especificadas a tipo numerico."""
    cleaned = df.copy()
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    return cleaned


def replace_missing_values(
    df: pd.DataFrame, replacements: dict[object, object]
) -> pd.DataFrame:
    """Reemplaza valores faltantes o marcadores equivalentes."""
    return df.replace(replacements).copy()


def clean_dataframe(
    df: pd.DataFrame,
    strip_strings: bool = True,
    standardize_columns: bool = True,
    remove_duplicates: bool = True,
    remove_empty_rows: bool = True,
    numeric_columns: list[str] | None = None,
    missing_value_replacements: dict[object, object] | None = None,
) -> pd.DataFrame:
    """Ejecuta un pipeline configurable de limpieza sobre un DataFrame."""
    cleaned = df.copy()

    if strip_strings:
        cleaned = trim_string_columns(cleaned)

    if standardize_columns:
        cleaned = standardize_column_names(cleaned)

    if remove_duplicates:
        cleaned = drop_duplicate_rows(cleaned)

    if remove_empty_rows:
        cleaned = drop_empty_rows(cleaned)

    if numeric_columns:
        target_columns = [
            normalize_column_name(column) if standardize_columns else column
            for column in numeric_columns
        ]
        cleaned = convert_numeric_columns(cleaned, target_columns)

    if missing_value_replacements:
        cleaned = replace_missing_values(cleaned, missing_value_replacements)

    return cleaned
