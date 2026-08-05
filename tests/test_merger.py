import pandas as pd
import pytest

from src.merger import (
    merge_multiple_datasets,
    merge_two_datasets,
    report_merge,
    validate_merge_keys,
)


def test_merge_preserves_rows():
    df1 = pd.DataFrame({"DIVIPOLA": ["05001", "05002"], "birth_rate": [10, 20]})
    df2 = pd.DataFrame({"DIVIPOLA": ["05001", "05002"], "poverty": [30, 40]})

    merged = merge_two_datasets(df1, df2)

    assert len(merged) == 2


def test_merge_missing_key_raises_error():
    df1 = pd.DataFrame({"codigo": ["05001"], "birth_rate": [10]})
    df2 = pd.DataFrame({"DIVIPOLA": ["05001"], "poverty": [30]})

    with pytest.raises(KeyError):
        merge_two_datasets(df1, df2)


def test_merge_keeps_expected_columns():
    df1 = pd.DataFrame({"DIVIPOLA": ["05001", "05002"], "birth_rate": [10, 20]})
    df2 = pd.DataFrame({"DIVIPOLA": ["05001", "05002"], "poverty": [30, 40]})

    merged = merge_two_datasets(df1, df2)

    assert set(merged.columns) == {"DIVIPOLA", "birth_rate", "poverty"}


def test_validate_merge_keys_accepts_valid_key():
    df1 = pd.DataFrame({"DIVIPOLA": ["05001"], "birth_rate": [10]})
    df2 = pd.DataFrame({"DIVIPOLA": ["05001"], "poverty": [30]})

    validate_merge_keys(df1, df2)


def test_merge_multiple_datasets_returns_master_dataframe():
    datasets = {
        "birth_rate": pd.DataFrame(
            {"DIVIPOLA": ["05001", "05002"], "birth_rate": [10, 20]}
        ),
        "poverty": pd.DataFrame({"DIVIPOLA": ["05001", "05002"], "poverty": [30, 40]}),
        "education": pd.DataFrame(
            {"DIVIPOLA": ["05001", "05002"], "education": [50, 60]}
        ),
    }

    master_df = merge_multiple_datasets(datasets)

    assert len(master_df) == 2
    assert set(master_df.columns) == {"DIVIPOLA", "birth_rate", "poverty", "education"}


def test_report_merge_returns_summary():
    df1 = pd.DataFrame({"DIVIPOLA": ["05001", "05002"], "birth_rate": [10, 20]})
    df2 = pd.DataFrame({"DIVIPOLA": ["05001", "05002"], "poverty": [30, 40]})
    merged = merge_two_datasets(df1, df2)

    report = report_merge(df1, df2, merged)

    assert report["merged_rows"] == 2
    assert report["lost_rows"] == 0
    assert report["new_columns"] == 1
    assert "MERGE REPORT" in report["report"]
