"""Funciones reutilizables para unir datasets de episodios."""

from __future__ import annotations

from typing import Any

import pandas as pd


def validate_merge_keys(
    left: pd.DataFrame, right: pd.DataFrame, key: str = "DIVIPOLA"
) -> None:
    """Valida que la llave de merge exista en ambos DataFrames."""
    missing = []
    if key not in left.columns:
        missing.append(f"left.{key}")
    if key not in right.columns:
        missing.append(f"right.{key}")

    if missing:
        raise KeyError(f"Merge key not found: {', '.join(missing)}")


def merge_two_datasets(
    left: pd.DataFrame,
    right: pd.DataFrame,
    key: str = "DIVIPOLA",
    how: str = "inner",
) -> pd.DataFrame:
    """Valida y une dos DataFrames usando una llave comun."""
    validate_merge_keys(left, right, key=key)
    return left.merge(right, on=key, how=how)


def merge_multiple_datasets(
    datasets: dict[str, pd.DataFrame],
    key: str = "DIVIPOLA",
    how: str = "inner",
) -> pd.DataFrame:
    """Une multiples DataFrames en un unico DataFrame maestro."""
    if not datasets:
        raise ValueError("At least one dataset is required for merging.")

    dataset_items = list(datasets.items())
    _, merged = dataset_items[0]

    for _, dataset in dataset_items[1:]:
        merged = merge_two_datasets(merged, dataset, key=key, how=how)

    return merged


def report_merge(
    left: pd.DataFrame,
    right: pd.DataFrame,
    merged: pd.DataFrame,
    key: str = "DIVIPOLA",
) -> dict[str, Any]:
    """Construye un resumen estructurado y legible de un merge."""
    left_rows = len(left)
    right_rows = len(right)
    merged_rows = len(merged)
    lost_rows = left_rows - merged_rows
    new_columns = len(
        [column for column in merged.columns if column not in left.columns]
    )
    success = lost_rows == 0

    lines = [
        "=" * 40,
        "MERGE REPORT",
        "=" * 40,
        "",
        f"Dataset 1: {left_rows} rows",
        f"Dataset 2: {right_rows} rows",
        "",
        f"Join key: {key}",
        "",
        f"Rows after merge: {merged_rows}",
        f"Lost rows: {lost_rows}",
        f"New columns: {new_columns}",
        "",
        "Status:",
        "OK Merge completed successfully." if success else "WARNING Merge lost rows.",
    ]

    return {
        "left_rows": left_rows,
        "right_rows": right_rows,
        "merged_rows": merged_rows,
        "lost_rows": lost_rows,
        "new_columns": new_columns,
        "key": key,
        "success": success,
        "report": "\n".join(lines),
    }
