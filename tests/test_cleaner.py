import pandas as pd

from src.cleaner import (
    clean_dataframe,
    convert_numeric_columns,
    drop_duplicate_rows,
    drop_empty_rows,
    replace_missing_values,
    standardize_column_names,
    trim_string_columns,
)


def test_cleaner_removes_fully_empty_rows():
    df = pd.DataFrame({"a": [1, None], "b": [2, None]})

    cleaned = drop_empty_rows(df)

    assert len(cleaned) == 1


def test_drop_duplicate_rows_removes_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})

    cleaned = drop_duplicate_rows(df)

    assert len(cleaned) == 2


def test_standardize_column_names_normalizes_headers():
    df = pd.DataFrame({"DIVIPOLA Code": ["05001"], "Nombre Municipio": ["Medellin"]})

    cleaned = standardize_column_names(df)

    assert list(cleaned.columns) == ["divipola_code", "nombre_municipio"]


def test_trim_string_columns_removes_surrounding_spaces():
    df = pd.DataFrame({"municipio": [" Medellin ", " Bogota "], "valor": [1, 2]})

    cleaned = trim_string_columns(df)

    assert cleaned["municipio"].tolist() == ["Medellin", "Bogota"]


def test_convert_numeric_columns_coerces_values():
    df = pd.DataFrame({"tasa": ["10.5", "11.7", "no-disponible"]})

    cleaned = convert_numeric_columns(df, ["tasa"])

    assert cleaned["tasa"].tolist()[:2] == [10.5, 11.7]
    assert pd.isna(cleaned["tasa"].iloc[2])


def test_replace_missing_values_updates_markers():
    df = pd.DataFrame({"internet": ["ND", "15", "Sin dato"]})

    cleaned = replace_missing_values(df, {"ND": None, "Sin dato": None})

    assert cleaned["internet"].isna().sum() == 2


def test_clean_dataframe_runs_generic_pipeline():
    df = pd.DataFrame(
        {
            " DIVIPOLA ": ["05001", "05001", None],
            " Municipio ": [" Medellin ", " Medellin ", None],
            " Tasa ": ["10.5", "10.5", None],
        }
    )

    cleaned = clean_dataframe(
        df,
        strip_strings=True,
        standardize_columns=True,
        remove_duplicates=True,
        remove_empty_rows=True,
        numeric_columns=["Tasa"],
    )

    assert list(cleaned.columns) == ["divipola", "municipio", "tasa"]
    assert len(cleaned) == 1
    assert cleaned["municipio"].iloc[0] == "Medellin"
    assert cleaned["tasa"].iloc[0] == 10.5
