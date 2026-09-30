from pathlib import Path
import pandas as pd

# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parents[1]

ARCHIVO = (
    BASE_DIR
    / "data"
    / "raw"
    / "censo_2018"
    / "antioquia"
    / "CNPV2018_5PER_A2_05.CSV"
)

SALIDA = (
    BASE_DIR
    / "data"
    / "interim"
    / "personas_medellin.csv"
)

# Variables necesarias para la primera inspección
COLUMNAS = [
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

SALIDA.parent.mkdir(parents=True, exist_ok=True)

# Medellín: departamento 05, municipio 001
filtro = lambda fila: (
    fila["U_DPTO"].astype(str).str.strip().eq("05")
    & fila["U_MPIO"].astype(str).str.strip().eq("001")
)

partes = []

for bloque in pd.read_csv(
    ARCHIVO,
    usecols=COLUMNAS,
    dtype=str,
    encoding="utf-8",
    chunksize=100_000,
    low_memory=False,
):
    medellin = bloque.loc[filtro(bloque)]

    if not medellin.empty:
        partes.append(medellin)

if partes:
    resultado = pd.concat(partes, ignore_index=True)
    resultado.to_csv(SALIDA, index=False, encoding="utf-8")

    print(f"Personas en Medellín: {len(resultado):,}")
    print(f"Archivo guardado en: {SALIDA}")
else:
    print("No se encontraron registros para Medellín.")