"""Diagnóstico y preparación de datos GIS.

Episodio 006 — Barrios de Medellín
"""

from pathlib import Path

import geopandas as gpd


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

def diagnosticar_capa(nombre: str, ruta: Path) -> None:
    """Lee una capa y muestra un diagnóstico inicial."""

    print("\n" + "=" * 70)
    print(f"DIAGNÓSTICO: {nombre.upper()}")
    print("=" * 70)

    if not ruta.exists():
        print(f"ERROR: no existe el archivo:")
        print(ruta)
        return

    print(f"Archivo: {ruta}")
    print(f"Tamaño: {ruta.stat().st_size / 1024:.1f} KB")

    try:
        gdf = gpd.read_file(ruta)

        print(f"\nRegistros: {len(gdf)}")
        print(f"Columnas: {len(gdf.columns)}")
        print(f"CRS: {gdf.crs}")
        print(f"Tipo de geometría:")
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
        else:
            print("  Campo no encontrado.")

        print("\nVALORES DE 'TIPO_AMENAZA':")
        if "tipo_amenaza" in gdf.columns:
            print(
                gdf["tipo_amenaza"]
                .value_counts(dropna=False)
                .to_string()
            )
        else:
            print("  Campo no encontrado.")

        print("\nVALORES FALTANTES:")
        faltantes = gdf.isna().sum()
        print(
            faltantes[faltantes > 0]
            .to_string()
            if (faltantes > 0).any()
            else "  No hay valores faltantes."
        )

        print("\nDUPLICADOS:")
        print(f"  Registros duplicados: {gdf.duplicated().sum()}")

        print("\nGEOMETRÍAS:")
        print(f"  Geometrías vacías: {gdf.geometry.is_empty.sum()}")
        print(f"  Geometrías nulas: {gdf.geometry.isna().sum()}")
        print(
            f"  Geometrías inválidas: "
            f"{(~gdf.geometry.is_valid).sum()}"
        )

        print("\nFECHAS:")
        for campo in ["fecha_adopcion", "fecha_actualizacion"]:
            if campo in gdf.columns:
                print(f"  {campo}:")
                print(
                    gdf[campo]
                    .head()
                    .to_string(index=False)
                )

    except Exception as error:
        print(f"\nERROR LEYENDO LA CAPA:")
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