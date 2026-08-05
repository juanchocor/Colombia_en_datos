import pandas as pd

from src.validator import (
    build_validation_report,
    validate_dataset,
    validate_duplicate_keys,
    validate_duplicate_rows,
    validate_missing_values,
    validate_numeric_columns,
    validate_required_columns,
)


def test_validate_required_columns():
    df = pd.DataFrame({"DIVIPOLA": ["001"], "tasa": [12.5]})

    missing = validate_required_columns(df, ["DIVIPOLA", "municipio", "tasa"])

    assert missing == ["municipio"]


def test_duplicate_rows_detection():
    df = pd.DataFrame(
        [
            {"DIVIPOLA": "001", "tasa": 1.2},
            {"DIVIPOLA": "001", "tasa": 1.2},
        ]
    )

    duplicates = validate_duplicate_rows(df)

    assert duplicates == 1


def test_duplicate_primary_key_detection():
    df = pd.DataFrame(
        [
            {"DIVIPOLA": "001", "tasa": 1.2},
            {"DIVIPOLA": "001", "tasa": 2.4},
        ]
    )

    duplicates = validate_duplicate_keys(df, "DIVIPOLA")

    assert duplicates == 1


def test_missing_values_detection():
    df = pd.DataFrame(
        {"DIVIPOLA": ["001", None], "tasa": [1.2, None], "municipio": ["A", "B"]}
    )

    missing_values = validate_missing_values(df)

    assert missing_values == 2


def test_numeric_columns_validation():
    df = pd.DataFrame({"tasa": ["10.5", "no-disponible"], "anio": [2020, 2021]})

    invalid_columns = validate_numeric_columns(df, ["tasa", "anio"])

    assert invalid_columns == ["tasa"]


def test_validate_dataset_returns_structured_results():
    df = pd.DataFrame(
        {
            "DIVIPOLA": ["001", "002"],
            "municipio": ["A", "B"],
            "tasa": [10.5, 12.3],
        }
    )

    results = validate_dataset(
        df,
        dataset_name="embarazo_adolescente.csv",
        required_columns=["DIVIPOLA", "municipio", "tasa"],
        key_column="DIVIPOLA",
        numeric_columns=["tasa"],
    )

    assert results["rows"] == 2
    assert results["columns"] == 3
    assert results["duplicate_rows"] == 0
    assert results["duplicate_keys"] == 0
    assert results["missing_values"] == 0
    assert results["missing_columns"] == []
    assert results["invalid_numeric_columns"] == []
    assert results["passed"] is True


def test_build_validation_report_contains_dataset_name():
    results = {
        "dataset_name": "embarazo_adolescente.csv",
        "rows": 2,
        "columns": 3,
        "duplicate_rows": 0,
        "duplicate_keys": 0,
        "missing_values": 0,
        "missing_columns": [],
        "invalid_numeric_columns": [],
        "empty_strings": 0,
        "passed": True,
    }

    report = build_validation_report(results)

    assert "DATA QUALITY REPORT" in report
    assert "embarazo_adolescente.csv" in report
