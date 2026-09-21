from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

EPISODIO_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = EPISODIO_DIR / "data" / "processed"
OUTPUT_DIR = EPISODIO_DIR / "outputs" / "tables"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CRS_ANALISIS = "EPSG:3116"


# ============================================================
# CAPAS
# ============================================================

CAPAS = {
    "inundaciones": PROCESSED_DIR / "inundaciones.geojson",
    "avenidas_torrenciales": PROCESSED_DIR / "avenidas_torrenciales.geojson",
    "movimientos_masa": PROCESSED_DIR / "movimientos_masa.geojson",
}


# ============================================================
# FUNCIÓN: VALIDAR ÁREA
# ============================================================

def validar_area(nombre, ruta):
    """Valida la consistencia del área de una capa GIS."""
    print("\n" + "=" * 70)
    print(f"VALIDACIÓN DE ÁREA: {nombre.upper()}")
    print("=" * 70)

    gdf = gpd.read_file(ruta)

    print(f"\nCRS original: {gdf.crs}")

    columnas_area = [
        col for col in gdf.columns
        if "st_area" in col.lower()
    ]

    if not columnas_area:
        print("⚠️ No se encontró una columna st_area.")
        return None

    columna_area = columnas_area[0]
    print(f"Columna de área oficial: {columna_area}")

    gdf["area_oficial_m2"] = pd.to_numeric(
        gdf[columna_area],
        errors="coerce",
    )
    gdf["area_oficial_ha"] = gdf["area_oficial_m2"] / 10_000

    gdf_proyectado = gdf.to_crs(CRS_ANALISIS)
    gdf["area_calculada_m2"] = gdf_proyectado.geometry.area
    gdf["area_calculada_ha"] = gdf["area_calculada_m2"] / 10_000

    gdf["diferencia_m2"] = (
        gdf["area_calculada_m2"] - gdf["area_oficial_m2"]
    )
    gdf["diferencia_ha"] = (
        gdf["area_calculada_ha"] - gdf["area_oficial_ha"]
    )

    gdf["diferencia_pct"] = np.where(
        gdf["area_oficial_m2"] > 0,
        (gdf["diferencia_m2"].abs() / gdf["area_oficial_m2"]) * 100,
        np.nan,
    )

    comparacion = gdf[
        [
            "area_oficial_ha",
            "area_calculada_ha",
            "diferencia_ha",
            "diferencia_pct",
        ]
    ].describe()

    print("\nResumen de diferencias porcentuales:")
    print(comparacion)

    print("\nMáxima diferencia porcentual:")
    print(gdf["diferencia_pct"].max())

    print("\nMediana de diferencia porcentual:")
    print(gdf["diferencia_pct"].median())

    print("\nDiferencia porcentual absoluta media:")
    print(gdf["diferencia_pct"].mean())

    casos_problematicos = (
        gdf[gdf["diferencia_pct"] > 1]
        .sort_values("diferencia_pct", ascending=False)
    )

    print(
        f"\nRegistros con diferencia > 1%: {len(casos_problematicos)}"
    )

    if len(casos_problematicos) > 0:
        print("\nTop 10 diferencias:")
        print(
            casos_problematicos[
                [
                    "codigo",
                    "nombre",
                    "riesgo",
                    "area_oficial_ha",
                    "area_calculada_ha",
                    "diferencia_pct",
                ]
            ].head(10).to_string(index=False)
        )

    total_oficial = gdf["area_oficial_ha"].sum()
    total_calculada = gdf["area_calculada_ha"].sum()
    diferencia_total = (
        abs(total_calculada - total_oficial)
        / total_oficial
        * 100
    )

    print("\nÁrea total:")
    print(f"  Oficial:    {total_oficial:,.2f} ha")
    print(f"  Calculada:  {total_calculada:,.2f} ha")
    print(f"  Diferencia: {diferencia_total:.4f}%")

    tabla = gdf[
        [
            "codigo",
            "nombre",
            "riesgo",
            "tipo_amenaza",
            "area_oficial_ha",
            "area_calculada_ha",
            "diferencia_ha",
            "diferencia_pct",
        ]
    ].copy()

    salida = OUTPUT_DIR / f"validacion_area_{nombre}.csv"
    tabla.to_csv(
        salida,
        index=False,
        encoding="utf-8-sig",
    )

    print("\nTabla guardada en:")
    print(salida)

    return gdf


# ============================================================
# FUNCIÓN: CONSTRUIR BASE DE RIESGO NO MITIGABLE
# ============================================================

def construir_base_riesgo_no_mitigable(resultados):
    """Agrupa las capas de riesgo con clasificación oficial alto riesgo no mitigable."""
    capas_riesgo = []

    for nombre, gdf in resultados.items():
        if gdf is None:
            continue

        filtro = (
            gdf["riesgo"]
            .astype(str)
            .str.strip()
            .str.lower()
            == "alto riesgo no mitigable".lower()
        )

        capa = gdf.loc[filtro].copy()
        capa["amenaza_origen"] = nombre
        capas_riesgo.append(capa)

        print(
            f"\n{nombre}: {len(capa)} polígonos de alto riesgo no mitigable"
        )

    if not capas_riesgo:
        raise ValueError(
            "No se encontraron polígonos de alto riesgo no mitigable."
        )

    riesgo = gpd.GeoDataFrame(
        pd.concat(capas_riesgo, ignore_index=True),
        crs=capas_riesgo[0].crs,
    )

    riesgo_proyectado = riesgo.to_crs(CRS_ANALISIS)
    riesgo["area_calculada_m2"] = riesgo_proyectado.geometry.area
    riesgo["area_calculada_ha"] = riesgo["area_calculada_m2"] / 10_000

    print("\n" + "=" * 70)
    print("BASE CONSOLIDADA: ALTO RIESGO NO MITIGABLE")
    print("=" * 70)

    print(f"\nTotal de polígonos: {len(riesgo)}")
    print("\nPolígonos por amenaza:")
    print(riesgo["amenaza_origen"].value_counts().to_string())

    print("\nSuperficie por amenaza:")
    resumen = (
        riesgo.groupby("amenaza_origen", as_index=False)
        .agg(
            poligonos=("geometry", "count"),
            hectareas=("area_calculada_ha", "sum"),
        )
        .sort_values("hectareas", ascending=False)
    )
    print(resumen.to_string(index=False))

    print(
        f"\nSuperficie total de los polígonos: "
        f"{riesgo['area_calculada_ha'].sum():,.2f} ha"
    )

    salida_geojson = PROCESSED_DIR / "alto_riesgo_no_mitigable.geojson"
    riesgo.to_file(salida_geojson, driver="GeoJSON")

    print("\nCapa guardada en:")
    print(salida_geojson)

    salida_csv = OUTPUT_DIR / "alto_riesgo_no_mitigable_por_amenaza.csv"
    resumen.to_csv(
        salida_csv,
        index=False,
        encoding="utf-8-sig",
    )

    print("\nResumen guardado en:")
    print(salida_csv)

    return riesgo

# ============================================================
# ANÁLISIS DE SOLAPAMIENTO ENTRE AMENAZAS
# ============================================================

def analizar_solapamiento(riesgo):
    """
    Calcula la superficie única de alto riesgo no mitigable
    y analiza cuántas amenazas se superponen espacialmente.

    La unidad de análisis es la superficie.
    """

    print("\n" + "=" * 70)
    print("ANÁLISIS DE SOLAPAMIENTO ENTRE AMENAZAS")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Proyectar a CRS métrico
    # --------------------------------------------------------

    riesgo_proj = riesgo.to_crs(CRS_ANALISIS).copy()

    # --------------------------------------------------------
    # 2. Unir todos los polígonos
    # --------------------------------------------------------

    geometria_unica = riesgo_proj.geometry.union_all()

    superficie_unica_m2 = geometria_unica.area
    superficie_unica_ha = superficie_unica_m2 / 10_000

    superficie_suma = riesgo_proj["area_calculada_ha"].sum()

    # --------------------------------------------------------
    # 3. Diferencia por solapamiento
    # --------------------------------------------------------

    superficie_duplicada = (
        superficie_suma - superficie_unica_ha
    )

    porcentaje_duplicacion = (
        superficie_duplicada
        / superficie_suma
        * 100
    )

    print(f"\nSuperficie sumada por polígonos: "
          f"{superficie_suma:,.2f} ha")

    print(f"Superficie única después de unir: "
          f"{superficie_unica_ha:,.2f} ha")

    print(f"Superficie contabilizada más de una vez: "
          f"{superficie_duplicada:,.2f} ha")

    print(f"Porcentaje de la suma explicado por "
          f"solapamientos: {porcentaje_duplicacion:.2f}%")

    # --------------------------------------------------------
    # 4. Solapamiento entre amenazas
    # --------------------------------------------------------

    amenazas = riesgo_proj["amenaza_origen"].unique()

    print("\nAmenazas encontradas:")
    for amenaza in amenazas:
        print(f"  - {amenaza}")

    # --------------------------------------------------------
    # 5. Intersecciones por pares
    # --------------------------------------------------------

    print("\nSolapamientos entre pares de amenazas:")

    resultados_pares = []

    for i in range(len(amenazas)):
        for j in range(i + 1, len(amenazas)):

            amenaza_a = amenazas[i]
            amenaza_b = amenazas[j]

            capa_a = riesgo_proj[
                riesgo_proj["amenaza_origen"] == amenaza_a
            ]

            capa_b = riesgo_proj[
                riesgo_proj["amenaza_origen"] == amenaza_b
            ]

            # Unión de cada amenaza antes de cruzarlas.
            # Esto evita contar varias veces el mismo espacio
            # dentro de una misma amenaza.

            geom_a = capa_a.geometry.union_all()
            geom_b = capa_b.geometry.union_all()

            interseccion = geom_a.intersection(geom_b)

            area_ha = interseccion.area / 10_000

            resultados_pares.append({
                "amenaza_a": amenaza_a,
                "amenaza_b": amenaza_b,
                "hectareas_solapadas": area_ha
            })

            print(
                f"  {amenaza_a} × {amenaza_b}: "
                f"{area_ha:,.2f} ha"
            )

    pares = pd.DataFrame(resultados_pares)

    # --------------------------------------------------------
    # 6. Guardar resultados
    # --------------------------------------------------------

    salida = OUTPUT_DIR / "solapamiento_amenazas.csv"

    pares.to_csv(
        salida,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nTabla de solapamientos guardada en:")
    print(salida)

    # --------------------------------------------------------
    # 7. Resumen general
    # --------------------------------------------------------

    resumen = pd.DataFrame([{
        "superficie_suma_ha": superficie_suma,
        "superficie_unica_ha": superficie_unica_ha,
        "superficie_duplicada_ha": superficie_duplicada,
        "porcentaje_duplicacion": porcentaje_duplicacion
    }])

    salida_resumen = (
        OUTPUT_DIR /
        "resumen_superficie_riesgo.csv"
    )

    resumen.to_csv(
        salida_resumen,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nResumen general guardado en:")
    print(salida_resumen)

    return geometria_unica, pares, resumen

# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    resultados = {}

    for nombre, ruta in CAPAS.items():
        if not ruta.exists():
            print(f"\n⚠️ No existe: {ruta}")
            continue

        resultados[nombre] = validar_area(nombre, ruta)

    riesgo_no_mitigable = (
        construir_base_riesgo_no_mitigable(resultados)
    )

    analizar_solapamiento(riesgo_no_mitigable)

    print("\n" + "=" * 70)
    print("PROCESO COMPLETO TERMINADO")
    print("=" * 70)

# De las 271,04 ha que resultan de sumar los polígonos de las tres amenazas,
# ¿cuánta superficie es realmente única y cuánta está siendo contada más de una vez?

