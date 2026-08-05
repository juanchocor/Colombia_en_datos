import pandas as pd

from src.statistics import summarize_numeric


def test_statistics_returns_summary_for_numeric_columns():
    df = pd.DataFrame({"valor": [1, 2, 3], "tasa": [0.1, 0.2, 0.3]})

    summary = summarize_numeric(df)

    assert "mean" in summary.columns
    assert "valor" in summary.index
