"""Preparacion de la dimension de cobertura de acueducto."""

import pandas as pd
from pathlib import Path


# ============================================================
# RUTAS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = RAW_DIR / "cobertura_acueducto_2018.csv"
OUTPUT_FILE = PROCESSED_DIR / "cobertura_acueducto_2018_procesada.csv"


# ============================================================
# CARGAR DATOS
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    dtype={
        "MPIO_CCDGO": str,
        "DPTO_CCDGO": str
    }
)

print("\n--- DATOS ORIGINALES ---")
print(f"Registros: {len(df)}")


# ============================================================
# REVISAR NULOS
# ============================================================

print("\n--- VALORES NULOS ---")
print(df.isna().sum())


# ============================================================
# VARIABLES DE VIVIENDAS
# ============================================================

df["viviendas_con_acueducto"] = df["CL0_AC_TU1"]

df["viviendas_sin_acueducto"] = df["CL0_AC_TU2"]

df["viviendas_total"] = (
    df["viviendas_con_acueducto"]
    + df["viviendas_sin_acueducto"]
)


# ============================================================
# COBERTURA
# ============================================================

df["cobertura_acueducto_pct"] = (
    df["viviendas_con_acueducto"]
    / df["viviendas_total"]
    * 100
)

df["sin_cobertura_pct"] = (
    df["viviendas_sin_acueducto"]
    / df["viviendas_total"]
    * 100
)


# ============================================================
# DIAGNÓSTICO
# ============================================================

print("\n--- DIAGNÓSTICO DE COBERTURA ---")

print(
    df[
        [
            "MPIO_CCDGO",
            "viviendas_con_acueducto",
            "viviendas_sin_acueducto",
            "viviendas_total",
            "cobertura_acueducto_pct",
            "sin_cobertura_pct"
        ]
    ].head()
)


print("\nEstadísticas de cobertura:")

print(
    df["cobertura_acueducto_pct"].describe()
)


print("\nCobertura mínima:")
print(
    df.loc[
        df["cobertura_acueducto_pct"].idxmin(),
        [
            "MPIO_CCDGO",
            "cobertura_acueducto_pct",
            "sin_cobertura_pct"
        ]
    ]
)


print("\nCobertura máxima:")
print(
    df.loc[
        df["cobertura_acueducto_pct"].idxmax(),
        [
            "MPIO_CCDGO",
            "cobertura_acueducto_pct",
            "sin_cobertura_pct"
        ]
    ]
)


# ============================================================
# GUARDAR
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nArchivo guardado en:")
print(OUTPUT_FILE)
