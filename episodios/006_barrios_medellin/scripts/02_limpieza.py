"""Diagnóstico y preparación de datos GIS.

Episodio 006 — Barrios de Medellín
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd


# ---------------------------------------------------------
# RUTAS
# ---------------------------------------------------------

EPISODIO_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = EPISODIO_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


# ---------------------------------------------------------
# ARCHIVOS
# ---------------------------------------------------------

CAPAS = {
    "inundaciones": RAW_DIR / "riesgo_inundaciones.geojson",
    "avenidas_torrenciales": RAW_DIR / "riesgo_avenidas_torrenciales.geojson",
    "movimientos_masa": RAW_DIR / "riesgo_movimientos_masa.geojson",
}


# ---------------------------------------------------------
# FUNCIONES
# ---------------------------------------------------------
def normalizar_capa(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Normaliza campos sin alterar la información original."""

    gdf = gdf.copy()

    # -------------------------------------------------
    # NORMALIZAR CATEGORÍAS DE RIESGO
    # -------------------------------------------------

    if "riesgo" in gdf.columns:
        gdf["riesgo"] = (
            gdf["riesgo"]
            .astype("string")
            .str.strip()
            .str.lower()
        )

        mapa_riesgo = {
            "alto riesgo no mitigable": "Alto riesgo no mitigable",
            "alto riesgo mitigable": "Alto riesgo mitigable",
            "con condiciones de riesgo": "Con condiciones de riesgo",
            "riesgo bajo": "Riesgo bajo",
            "riesgo medio": "Riesgo medio",
        }

        gdf["riesgo"] = gdf["riesgo"].replace(
            mapa_riesgo
        )

    # -------------------------------------------------
    # CONVERTIR FECHAS
    # -------------------------------------------------

    for campo in [
        "fecha_adopcion",
        "fecha_actualizacion",
    ]:
        if campo in gdf.columns:
            gdf[campo] = pd.to_datetime(
                gdf[campo],
                unit="ms",
                errors="coerce",
            )

    return gdf


def diagnosticar_capa(nombre: str, ruta: Path) -> None:
    """Lee una capa y muestra un diagnóstico inicial."""

    print("\n" + "=" * 70)
    print(f"DIAGNÓSTICO: {nombre.upper()}")
    print("=" * 70)

    if not ruta.exists():
        print("ERROR: no existe el archivo:")
        print(ruta)
        return

    print(f"Archivo: {ruta}")
    print(f"Tamaño: {ruta.stat().st_size / 1024:.1f} KB")

    try:
        gdf = gpd.read_file(ruta)
        gdf = normalizar_capa(gdf)

        print(f"\nRegistros: {len(gdf)}")
        print(f"Columnas: {len(gdf.columns)}")
        print(f"CRS: {gdf.crs}")

        print("\nTIPO DE GEOMETRÍA:")
        print(gdf.geometry.geom_type.value_counts().to_string())

        print("\nCOLUMNAS:")
        for columna in gdf.columns:
            print(f"  - {columna}")

        print("\nVALORES DE 'RIESGO':")
        if "riesgo" in gdf.columns:
            print(
                gdf["riesgo"]
                .value_counts(dropna=False)
                .to_string()
            )

        print("\nVALORES DE 'TIPO_AMENAZA':")
        if "tipo_amenaza" in gdf.columns:
            print(
                gdf["tipo_amenaza"]
                .value_counts(dropna=False)
                .to_string()
            )

        # -------------------------------------------------
        # FECHAS
        # -------------------------------------------------

        print("\nFECHAS:")

        for campo in [
            "fecha_adopcion",
            "fecha_actualizacion",
        ]:
            if campo in gdf.columns:

                fechas = gdf[campo].dropna()

                # ArcGIS entrega estas fechas como
                # milisegundos desde 1970-01-01.
                fechas = pd.to_datetime(
                    fechas,
                    unit="ms",
                    errors="coerce",
                )

                print(f"\n{campo}:")
                print(
                    fechas
                    .dt.strftime("%Y-%m-%d")
                    .value_counts()
                    .sort_index()
                    .to_string()
                )

        # -------------------------------------------------
        # ÁREA
        # -------------------------------------------------

        print("\nÁREA POR CATEGORÍA DE RIESGO:")

        if "riesgo" in gdf.columns:

            # La capa viene en EPSG:4326.
            # Para calcular áreas debemos usar
            # un CRS proyectado en metros.
            gdf_metrico = gdf.to_crs(
                "EPSG:3116"
            )

            gdf_metrico["area_m2"] = (
                gdf_metrico.geometry.area
            )

            resumen_area = (
                gdf_metrico
                .groupby("riesgo")["area_m2"]
                .agg(
                    cantidad="count",
                    area_m2="sum",
                )
                .sort_values(
                    "area_m2",
                    ascending=False,
                )
            )

            resumen_area["area_ha"] = (
                resumen_area["area_m2"] / 10_000
            )

            print(
                resumen_area.to_string(
                    float_format=lambda x: f"{x:,.2f}"
                )
            )

        # -------------------------------------------------
        # CALIDAD
        # -------------------------------------------------

        print("\nVALORES FALTANTES:")

        faltantes = gdf.isna().sum()

        if (faltantes > 0).any():
            print(
                faltantes[faltantes > 0]
                .to_string()
            )
        else:
            print("  No hay valores faltantes.")

        print("\nDUPLICADOS:")
        print(
            f"  Registros duplicados: "
            f"{gdf.duplicated().sum()}"
        )

        print("\nGEOMETRÍAS:")
        print(
            f"  Geometrías vacías: "
            f"{gdf.geometry.is_empty.sum()}"
        )
        print(
            f"  Geometrías nulas: "
            f"{gdf.geometry.isna().sum()}"
        )
        print(
            f"  Geometrías inválidas: "
            f"{(~gdf.geometry.is_valid).sum()}"
        )

                # -------------------------------------------------
        # GUARDAR COPIA PROCESADA
        # -------------------------------------------------

        nombre_procesado = (
            f"{nombre}.geojson"
        )

        ruta_procesada = (
            PROCESSED_DIR / nombre_procesado
        )

        gdf.to_file(
            ruta_procesada,
            driver="GeoJSON",
        )

        print("\nCOPIA PROCESADA:")
        print(ruta_procesada)

    except Exception as error:
        print("\nERROR LEYENDO LA CAPA:")
        print(error)




# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main() -> None:
    """Ejecuta el diagnóstico de las capas descargadas."""

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 70)
    print("COLOMBIA EN DATOS — EPISODIO 006")
    print("DIAGNÓSTICO DE DATOS GIS")
    print("=" * 70)

    print(f"\nRAW:")
    print(RAW_DIR)

    print(f"\nPROCESSED:")
    print(PROCESSED_DIR)

    for nombre, ruta in CAPAS.items():
        diagnosticar_capa(
            nombre=nombre,
            ruta=ruta,
        )


if __name__ == "__main__":
    main()