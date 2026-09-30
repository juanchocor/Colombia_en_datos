import requests
import geopandas as gpd
from pathlib import Path
from shapely.geometry import shape


# ============================================================
# RUTAS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RAW_DIR / "geometria_municipal_2018.geojson"


# ============================================================
# FUENTE DANE
# ============================================================

URL = (
    "https://geoportal.dane.gov.co/mparcgis/rest/services/"
    "MGN2018/Serv_CapaMunicipiosInt_2018/MapServer/0/query"
)


# ============================================================
# DESCARGA POR BLOQUES
# ============================================================

BLOQUE = 100
offset = 0

todos_los_registros = []

print("Consultando geometría municipal DANE...")
print(f"Bloque de consulta: {BLOQUE} registros")


while True:

    print(f"\nConsultando registros desde {offset}...")

    params = {
        "where": "1=1",
        "outFields": (
            "OBJECTID,"
            "DPTO_CCDGO,"
            "MPIO_CCDGO,"
            "MPIO_CDPMP,"
            "MPIO_CNMBR"
        ),
        "returnGeometry": "true",
        "resultOffset": offset,
        "resultRecordCount": BLOQUE,
        "f": "json"
    }

    response = requests.get(URL, params=params, timeout=120)

    print("STATUS HTTP:", response.status_code)

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        print("\nERROR DANE:")
        print(data["error"])
        raise RuntimeError("El servicio devolvió un error.")

    features = data.get("features", [])

    print("Registros recibidos:", len(features))

    if not features:
        break

    todos_los_registros.extend(features)

    if len(features) < BLOQUE:
        print("Último bloque alcanzado.")
        break

    offset += BLOQUE


# ============================================================
# VERIFICACIÓN DE DESCARGA
# ============================================================

print("\n--- DESCARGA COMPLETA ---")
print("Registros totales:", len(todos_los_registros))


# ============================================================
# CONSTRUIR GEOMETRÍAS
# ============================================================

registros = []

for feature in todos_los_registros:

    atributos = feature["attributes"]
    geometria = feature.get("geometry")

    if geometria is None:
        continue

    # ArcGIS devuelve los polígonos como "rings"
    polygon = {
        "type": "Polygon",
        "coordinates": geometria["rings"]
    }

    atributos["geometry"] = shape(polygon)

    registros.append(atributos)


gdf = gpd.GeoDataFrame(
    registros,
    geometry="geometry",
    crs="EPSG:3857"
)


# ============================================================
# TRANSFORMAR A WGS84
# ============================================================

gdf = gdf.to_crs("EPSG:4326")


# ============================================================
# DIAGNÓSTICO
# ============================================================

print("\n--- DIAGNÓSTICO ---")

print("Registros:", len(gdf))
print("Municipios únicos:", gdf["MPIO_CDPMP"].nunique())
print("CRS:", gdf.crs)

print("\nGeometrías nulas:")
print(gdf.geometry.isna().sum())

print("\nTipos de geometría:")
print(gdf.geometry.geom_type.value_counts())

print("\nPrimeros registros:")
print(
    gdf[
        [
            "DPTO_CCDGO",
            "MPIO_CCDGO",
            "MPIO_CDPMP",
            "MPIO_CNMBR"
        ]
    ].head()
)


# ============================================================
# DUPLICADOS
# ============================================================

duplicados = gdf["MPIO_CDPMP"].duplicated().sum()

print("\nCódigos municipales duplicados:", duplicados)


# ============================================================
# GUARDAR
# ============================================================

gdf.to_file(
    OUTPUT_FILE,
    driver="GeoJSON"
)

print("\nArchivo guardado en:")
print(OUTPUT_FILE)