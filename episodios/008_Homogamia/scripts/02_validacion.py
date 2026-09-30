"""Punto de entrada para validar archivos, variables y claves censales."""

from pathlib import Path
import pandas as pd

# ============================================================
# RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

ARCHIVO = (
    BASE_DIR
    / "data"
    / "interim"
    / "personas_medellin.csv"
)

SALIDA = BASE_DIR / "outputs" / "tables"
SALIDA.mkdir(parents=True, exist_ok=True)

# ============================================================
# CARGA
# ============================================================

COLUMNAS_CLAVE = [
    "U_DPTO",
    "U_MPIO",
    "UA_CLASE",
    "COD_ENCUESTAS",
    "U_VIVIENDA",
    "P_NROHOG",
    "P_NRO_PER",
    "P_SEXO",
    "P_EDADR",
    "P_PARENTESCOR",
    "PA1_GRP_ETNIC",
    "P_EST_CIVIL",
]

print("Leyendo archivo de Medellín...")

df = pd.read_csv(
    ARCHIVO,
    usecols=COLUMNAS_CLAVE,
    dtype=str,
    encoding="utf-8"
)

print(f"Registros cargados: {len(df):,}")

# ============================================================
# 1. VALIDACIÓN GEOGRÁFICA
# ============================================================

print("\n--- VALIDACIÓN GEOGRÁFICA ---")

print("Departamentos encontrados:")
print(df["U_DPTO"].value_counts(dropna=False))

print("\nMunicipios encontrados:")
print(df["U_MPIO"].value_counts(dropna=False))

# ============================================================
# 2. VALORES FALTANTES
# ============================================================

print("\n--- VALORES FALTANTES ---")

faltantes = (
    df[COLUMNAS_CLAVE]
    .isna()
    .sum()
    .rename("valores_faltantes")
    .to_frame()
)

faltantes["porcentaje"] = (
    faltantes["valores_faltantes"] / len(df) * 100
).round(2)

print(faltantes)

faltantes.to_csv(
    SALIDA / "faltantes_medellin.csv",
    encoding="utf-8-sig"
)

# ============================================================
# 3. DUPLICADOS
# ============================================================

print("\n--- DUPLICADOS ---")

duplicados_exactos = df.duplicated().sum()

print(f"Duplicados exactos: {duplicados_exactos:,}")

CLAVE_PERSONA = [
    "U_DPTO",
    "U_MPIO",
    "UA_CLASE",
    "COD_ENCUESTAS",
    "U_VIVIENDA",
    "P_NROHOG",
    "P_NRO_PER",
]

duplicados_clave = df.duplicated(
    subset=CLAVE_PERSONA
).sum()

print(f"Duplicados por clave de persona: {duplicados_clave:,}")

# ============================================================
# 4. FRECUENCIAS DE VARIABLES CLAVE
# ============================================================

VARIABLES = [
    "P_SEXO",
    "P_EDADR",
    "P_PARENTESCOR",
    "PA1_GRP_ETNIC",
    "P_EST_CIVIL",
]

for variable in VARIABLES:
    print(f"\n--- DISTRIBUCIÓN: {variable} ---")

    frecuencias = (
        df[variable]
        .value_counts(dropna=False)
        .rename_axis(variable)
        .reset_index(name="personas")
    )

    frecuencias["porcentaje"] = (
        frecuencias["personas"] / len(df) * 100
    ).round(2)

    print(frecuencias.to_string(index=False))

    frecuencias.to_csv(
        SALIDA / f"frecuencia_{variable.lower()}_medellin.csv",
        index=False,
        encoding="utf-8-sig"
    )

# ============================================================
# 5. VALIDACIÓN DE LA CLAVE
# ============================================================

print("\n--- REGISTROS SIN CLAVE COMPLETA ---")

sin_clave = df[CLAVE_PERSONA].isna().any(axis=1).sum()

print(f"Personas con algún campo de clave faltante: {sin_clave:,}")

# ============================================================
# RESULTADO
# ============================================================

print("\nValidación finalizada.")
print(f"Tablas guardadas en: {SALIDA}")