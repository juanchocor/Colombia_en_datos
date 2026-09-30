"""Registro y descubrimiento de fuentes del episodio 007."""

import requests
import pandas as pd
from pathlib import Path


# ============================================================
# RUTAS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RAW_DIR / "cobertura_acueducto_2018.csv"


# ============================================================
# FUENTE DANE
# ============================================================

URL = (
    "https://geoportal.dane.gov.co/mparcgis/rest/services/"
    "INDICADORES_VIVIENDA/"
    "Serv_Mpios_CoberturaAcueducto_Ano_2018/"
    "MapServer/1/query"
)


# ============================================================
# DESCARGA PAGINADA
# ============================================================

registros = []
offset = 0
limite = 1000

while True:

    print(f"Consultando registros desde {offset}...")

    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "false",
        "resultOffset": offset,
        "resultRecordCount": limite,
        "f": "json"
    }

    response = requests.get(
        URL,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    features = data.get("features", [])

    if not features:
        break

    for feature in features:
        registros.append(feature["attributes"])

    print(f"  Registros recibidos: {len(features)}")

    if not data.get("exceededTransferLimit", False):
        break

    offset += limite


# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame(registros)


# ============================================================
# DIAGNÓSTICO
# ============================================================

print("\n--- DIAGNÓSTICO FINAL ---")

print(f"Total registros: {len(df)}")

print("\nColumnas:")
print(df.columns.tolist())

print("\nPrimeros registros:")
print(df.head())

print("\nMunicipios únicos:")
print(df["MPIO_CCDGO"].nunique())

print("\nValores nulos:")
print(df.isna().sum())


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