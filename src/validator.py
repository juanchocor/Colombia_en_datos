"""Funciones de validacion de calidad de datos."""

from __future__ import annotations

from typing import Any

import pandas as pd


def validate_required_columns(
    df: pd.DataFrame, required_columns: list[str]
) -> list[str]:
    """Devuelve las columnas requeridas que faltan en el DataFrame."""
    return [column for column in required_columns if column not in df.columns]


def validate_duplicate_rows(df: pd.DataFrame) -> int:
    """Cuenta filas duplicadas exactas."""
    return int(df.duplicated().sum())


def validate_duplicate_keys(df: pd.DataFrame, key_column: str) -> int:
    """Cuenta valores duplicados en una columna llave."""
    if key_column not in df.columns:
        raise KeyError(f"Key column not found: {key_column}")

    return int(df.duplicated(subset=[key_column]).sum())


def validate_missing_values(df: pd.DataFrame) -> int:
    """Cuenta el total de valores faltantes en el DataFrame."""
    return int(df.isna().sum().sum())


def validate_numeric_columns(df: pd.DataFrame, numeric_columns: list[str]) -> list[str]:
    """Detecta columnas que no son totalmente convertibles a numerico."""
    invalid_columns: list[str] = []

    for column in numeric_columns:
        if column not in df.columns:
            invalid_columns.append(column)
            continue

        non_null_values = df[column].dropna()
        converted = pd.to_numeric(non_null_values, errors="coerce")
        if converted.isna().any():
            invalid_columns.append(column)

    return invalid_columns


def build_validation_report(results: dict[str, Any]) -> str:
    """Construye un reporte legible a partir del resultado estructurado."""
    lines = [
        "=" * 52,
        "DATA QUALITY REPORT",
        "=" * 52,
        "",
        f"Dataset: {results['dataset_name']}",
        "",
        f"Rows: {results['rows']}",
        f"Columns: {results['columns']}",
        "",
    ]

    if results["duplicate_rows"] == 0:
        lines.append("✔ No duplicate rows")
    else:
        lines.append(f"⚠ Duplicate rows: {results['duplicate_rows']}")

    if results["duplicate_keys"] == 0:
        lines.append("✔ No duplicate primary keys")
    else:
        lines.append(f"⚠ Duplicate primary keys: {results['duplicate_keys']}")

    if not results["missing_columns"]:
        lines.append("✔ Required columns present")
    else:
        lines.append(f"⚠ Missing columns: {', '.join(results['missing_columns'])}")

    if not results["invalid_numeric_columns"]:
        lines.append("✔ Numeric columns correctly typed")
    else:
        lines.append(
            "⚠ Invalid numeric columns: "
            + ", ".join(results["invalid_numeric_columns"])
        )

    if results["missing_values"] == 0:
        lines.append("✔ No missing values")
    else:
        lines.append(f"⚠ Missing values: {results['missing_values']}")

    if results["empty_strings"] == 0:
        lines.append("✔ No empty strings")
    else:
        lines.append(f"⚠ Empty strings: {results['empty_strings']}")

    if results["passed"]:
        lines.append("✔ Passed validation")
    else:
        lines.append("⚠ Validation issues found")

    return "\n".join(lines)


def validate_dataset(
    df: pd.DataFrame,
    dataset_name: str = "dataset.csv",
    required_columns: list[str] | None = None,
    key_column: str | None = None,
    numeric_columns: list[str] | None = None,
) -> dict[str, Any]:
    """Ejecuta la validacion completa y devuelve un resultado estructurado."""
    required_columns = required_columns or []
    numeric_columns = numeric_columns or []

    missing_columns = validate_required_columns(df, required_columns)
    duplicate_rows = validate_duplicate_rows(df)
    duplicate_keys = validate_duplicate_keys(df, key_column) if key_column else 0
    missing_values = validate_missing_values(df)
    invalid_numeric_columns = validate_numeric_columns(df, numeric_columns)
    empty_strings = int(
        (df.astype(str).apply(lambda col: col.str.strip() == "")).sum().sum()
    )

    passed = (
        duplicate_rows == 0
        and duplicate_keys == 0
        and missing_values == 0
        and empty_strings == 0
        and not missing_columns
        and not invalid_numeric_columns
    )

    results: dict[str, Any] = {
        "dataset_name": dataset_name,
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": duplicate_rows,
        "duplicate_keys": duplicate_keys,
        "missing_values": missing_values,
        "missing_columns": missing_columns,
        "invalid_numeric_columns": invalid_numeric_columns,
        "empty_strings": empty_strings,
        "passed": passed,
    }
    results["report"] = build_validation_report(results)
    return results
