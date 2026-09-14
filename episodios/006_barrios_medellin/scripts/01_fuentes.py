"""Descubrimiento de fuentes GIS.

Episodio 006 — Barrios de Medellín
"""

from pathlib import Path

import requests


# ---------------------------------------------------------
# RUTAS
# ---------------------------------------------------------

EPISODIO_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = EPISODIO_DIR / "data"
RAW_DIR = DATA_DIR / "raw"


# ---------------------------------------------------------
# FUENTES
# ---------------------------------------------------------

FUENTES = {
    "riesgo_pot": {
        "nombre": "Zona de condición de riesgo y alto riesgo no mitigable",
        "institucion": "Alcaldía de Medellín — Departamento Administrativo de Planeación",
        "url": (
            "https://www.medellin.gov.co/servidormapas/rest/services/"
            "ordenamiento_ter/VM_08_Zona_Condicion_Riego_Alto_Riesgo_NM/MapServer"
        ),
    }
}


# ---------------------------------------------------------
# FUNCIONES
# ---------------------------------------------------------

def consultar_servicio(nombre: str, url: str) -> None:
    """Consulta y muestra los metadatos de un servicio ArcGIS REST."""

    print("\n" + "=" * 70)
    print(f"FUENTE: {nombre}")
    print("=" * 70)
    print(f"URL: {url}")

    try:
        respuesta = requests.get(
            url,
            params={"f": "json"},
            timeout=30,
        )
        respuesta.raise_for_status()

        datos = respuesta.json()

        if "error" in datos:
            print("\nERROR DEL SERVICIO:")
            print(datos["error"])
            return

        print(f"\nNombre: {datos.get('name')}")
        print(f"Tipo: {datos.get('type')}")
        print(f"Descripción: {datos.get('description', '').strip()}")
        print(f"Referencia espacial: {datos.get('spatialReference')}")

        capas = datos.get("layers", [])

        print("\nCAPAS DISPONIBLES:")

        if not capas:
            print("  No hay capas en este nivel.")

        for capa in capas:
            print(
                f"  ID {capa.get('id')}: "
                f"{capa.get('name')}"
            )

    except requests.RequestException as error:
        print(f"\nERROR DE CONEXIÓN: {error}")


def inspeccionar_capa(url: str, capa_id: int) -> None:
    """Muestra los campos y metadatos de una capa ArcGIS."""

    capa_url = f"{url}/{capa_id}"

    try:
        respuesta = requests.get(
            capa_url,
            params={"f": "json"},
            timeout=30,
        )
        respuesta.raise_for_status()

        datos = respuesta.json()

        print("\n" + "-" * 70)
        print(f"CAPA ID: {capa_id}")
        print(f"NOMBRE: {datos.get('name')}")
        print("-" * 70)
        print(f"Geometría: {datos.get('geometryType')}")

        print("\nCAMPOS:")

        for campo in datos.get("fields", []):
            print(
                f"  - {campo.get('name')} "
                f"| alias: {campo.get('alias')} "
                f"| tipo: {campo.get('type')}"
            )

    except requests.RequestException as error:
        print(f"Error consultando capa {capa_id}: {error}")


def probar_consulta_capa(url: str, capa_id: int) -> None:
    """Prueba una consulta mínima a una capa ArcGIS."""

    consulta_url = f"{url}/{capa_id}/query"

    parametros = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "resultRecordCount": 1,
        "f": "geojson",
    }

    try:
        respuesta = requests.get(
            consulta_url,
            params=parametros,
            timeout=30,
        )
        respuesta.raise_for_status()

        datos = respuesta.json()

        print("\n" + "=" * 70)
        print(f"PRUEBA DE CONSULTA — CAPA {capa_id}")
        print("=" * 70)

        print(f"Tipo de respuesta: {datos.get('type')}")
        print(
            "Número de registros obtenidos: "
            f"{len(datos.get('features', []))}"
        )

        if "error" in datos:
            print("\nERROR DEVUELTO POR ARCGIS:")
            print(datos["error"])
            return

        if datos.get("features"):
            registro = datos["features"][0]

            print("\nATRIBUTOS DEL PRIMER REGISTRO:")

            for campo, valor in registro.get("properties", {}).items():
                print(f"  - {campo}: {valor}")

            print("\nGEOMETRÍA:")
            print(
                registro.get("geometry", {}).get("type")
            )

    except requests.RequestException as error:
        print(f"Error consultando capa {capa_id}: {error}")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main() -> None:
    """Ejecuta el descubrimiento inicial de fuentes."""

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 70)
    print("COLOMBIA EN DATOS — EPISODIO 006")
    print("BARRIOS DE MEDELLÍN")
    print("=" * 70)

    print("\nDirectorio del episodio:")
    print(EPISODIO_DIR)

    print("\nDirectorio de datos:")
    print(DATA_DIR)

    print("\nDirectorio RAW:")
    print(RAW_DIR)

    url_servicio = FUENTES["riesgo_pot"]["url"]

    consultar_servicio(
        nombre=FUENTES["riesgo_pot"]["nombre"],
        url=url_servicio,
    )

    for capa_id in [2, 3, 4]:
        inspeccionar_capa(
            url=url_servicio,
            capa_id=capa_id,
        )

    # Por ahora probamos solamente una capa.
    probar_consulta_capa(
        url=url_servicio,
        capa_id=4,
    )

    for capa_id in [2, 3, 4]:
        contar_registros_capa(
            url=url_servicio,
            capa_id=capa_id,
        )

    probar_consulta_capa(
    url=url_servicio,
    capa_id=3,
     
    )

    descargar_capa_geojson(
        url=url_servicio,
        capa_id=3,
        nombre_archivo="riesgo_avenidas_torrenciales.geojson",
    )

    descargar_capa_geojson(
        url=url_servicio,
        capa_id=4,
        nombre_archivo="riesgo_movimientos_masa.geojson",
    )    

#-------------------------------------------------------------------------
# Vamos a medir el tamaño de las capas para ver si es viable descargarlas.
#-------------------------------------------------------------------------

def contar_registros_capa(url: str, capa_id: int) -> None:
    """Consulta cuántos registros tiene una capa ArcGIS."""

    consulta_url = f"{url}/{capa_id}/query"

    parametros = {
        "where": "1=1",
        "returnCountOnly": "true",
        "f": "json",
    }

    try:
        respuesta = requests.get(
            consulta_url,
            params=parametros,
            timeout=30,
        )
        respuesta.raise_for_status()

        datos = respuesta.json()

        print("\n" + "-" * 70)
        print(f"CONTEO DE REGISTROS — CAPA {capa_id}")
        print("-" * 70)

        if "error" in datos:
            print("ERROR DEVUELTO POR ARCGIS:")
            print(datos["error"])
            return

        print(f"Total de registros: {datos.get('count')}")

    except requests.RequestException as error:
        print(f"Error contando registros de la capa {capa_id}: {error}")    

def descargar_capa_geojson(
    url: str,
    capa_id: int,
    nombre_archivo: str,
) -> None:
    """Descarga una capa ArcGIS completa en formato GeoJSON."""

    consulta_url = f"{url}/{capa_id}/query"

    parametros = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
    }

    try:
        print("\n" + "=" * 70)
        print(f"DESCARGANDO CAPA {capa_id}")
        print("=" * 70)

        respuesta = requests.get(
            consulta_url,
            params=parametros,
            timeout=120,
        )
        respuesta.raise_for_status()

        datos = respuesta.json()

        if "error" in datos:
            print("ERROR DEVUELTO POR ARCGIS:")
            print(datos["error"])
            return

        registros = datos.get("features", [])

        ruta_salida = RAW_DIR / nombre_archivo

        import json

        with open(
            ruta_salida,
            "w",
            encoding="utf-8",
        ) as archivo:
            json.dump(
                datos,
                archivo,
                ensure_ascii=False,
                indent=2,
            )

        print(f"Registros descargados: {len(registros)}")
        print(f"Archivo guardado en:")
        print(ruta_salida)

    except requests.RequestException as error:
        print(f"Error descargando la capa {capa_id}: {error}")

if __name__ == "__main__":
    main()
