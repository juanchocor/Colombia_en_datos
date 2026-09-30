from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

ARCHIVO = (
    BASE_DIR
    / "data"
    / "raw"
    / "censo_2018"
    / "antioquia"
    / "CNPV2018_5PER_A2_05.CSV"
)

df = pd.read_csv(
    ARCHIVO,
    sep=None,
    engine="python",
    encoding="utf-8",
    usecols=["U_DPTO", "U_MPIO"],
    dtype=str,
    nrows=20,
)

print("Columnas:", df.columns.tolist())

print("\nValores de U_DPTO:")
print([repr(x) for x in df["U_DPTO"].unique()])

print("\nValores de U_MPIO:")
print([repr(x) for x in df["U_MPIO"].unique()])

print("\nPrimeros registros:")
print(df.to_string(index=False))