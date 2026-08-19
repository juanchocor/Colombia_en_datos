"""Construye el Dataset 09 del IOT Chocó a partir de fuentes exclusivamente RAW.

La fuente SGP disponible contiene proyecciones/asignaciones para 2027. No se
interpreta como ejecución ni se territorializa la fuente SECOP departamental.
"""
from __future__ import annotations

import logging
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EPISODE = next(ROOT.joinpath("episodios").glob("002_EL_*"))
DATA = EPISODE / "Data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
LOG_DIR = EPISODE / "logs"
SOURCE_09 = next(RAW.glob("dataset_09_inversion_publica_infraestructura_*.xlsx"))
UNIVERSE = RAW / "dataset_01_poblacion_territorio_choco_definitivo.csv"
PROCESS_DATE = date.today().isoformat()


def setup_logger() -> logging.Logger:
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger("dataset_09")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler = logging.FileHandler(LOG_DIR / "dataset_09.log", encoding="utf-8")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def clean_divipola(series: pd.Series) -> pd.Series:
    return series.astype("string").str.replace(r"\.0$", "", regex=True).str.zfill(5)


def snake(text: str) -> str:
    text = text.lower().replace("<", "menor_que_").replace("-", " ")
    text = (text.replace("á", "a").replace("é", "e").replace("í", "i")
                .replace("ó", "o").replace("ú", "u").replace("ñ", "n"))
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", text)).strip("_")


def main() -> None:
    logger = setup_logger()
    PROCESSED.mkdir(exist_ok=True)
    logger.info("Inicio de construcción Dataset 09")
    raw_files = sorted(path for path in RAW.iterdir() if path.is_file())
    for path in raw_files:
        logger.info("Inventario RAW | archivo=%s | extension=%s | bytes=%s | modificado=%s",
                    path.name, path.suffix, path.stat().st_size,
                    date.fromtimestamp(path.stat().st_mtime).isoformat())
    logger.info("RAW revisado: %s", SOURCE_09.name)
    logger.info("Universo territorial: %s", UNIVERSE.name)

    universe = pd.read_csv(UNIVERSE, dtype={"divipola": "string"})
    universe["divipola"] = clean_divipola(universe["divipola"])
    universe = universe[["divipola", "municipio", "departamento"]].copy()
    if universe["divipola"].duplicated().any() or len(universe) != 31:
        raise ValueError("El universo IOT debe tener 31 DIVIPOLA únicos.")

    # En la hoja, las filas 0 y 1 son total nacional y una fila vacía; la fila 2 es cabecera.
    excel = pd.ExcelFile(SOURCE_09)
    logger.info("Hojas del archivo Dataset 09: %s", ", ".join(excel.sheet_names))
    sgp = pd.read_excel(excel, sheet_name="SGP_2027_SGP", header=2, dtype={"DANE": "string"})
    logger.info("Hoja SGP_2027_SGP inspeccionada: %s filas, %s columnas", *sgp.shape)
    sgp["divipola"] = clean_divipola(sgp["DANE"])
    sgp_choco = sgp[sgp["divipola"].str.startswith("27", na=False)].copy()
    sgp_dept = sgp_choco[sgp_choco["divipola"] == "27000"].copy()
    sgp_municipal = sgp_choco[sgp_choco["divipola"] != "27000"].copy()
    logger.info("SGP Chocó: %s registros; municipal: %s; agregado departamental excluido: %s",
                len(sgp_choco), len(sgp_municipal), len(sgp_dept))

    source_components = [
        "POBLACIÓN ATENDIDA", "CALIDAD (GRATUIDAD)", "CALIDAD (MATRÍCULA)",
        "RÉGIMEN SUBSIDIADO", "SALUD PÚBLICA", "SUBSIDIO A LA OFERTA",
        "AGUA POTABLE", "POBLACIÓN <25MIL", "POBREZA <25 MIL",
        "POBLACIÓN - GENERAL", "POBREZA - GENERAL", "RIBEREÑOS",
        "ALIMENTACIÓN ESCOLAR",
    ]
    renamed = {column: f"sgp_2027_{snake(column)}" for column in source_components}
    for column in source_components:
        sgp_municipal[column] = pd.to_numeric(sgp_municipal[column], errors="coerce")
        if sgp_municipal[column].isna().any():
            raise ValueError(f"Componente SGP no numérico o nulo: {column}")
    sgp_municipal = sgp_municipal.rename(columns=renamed)
    component_columns = list(renamed.values())
    sgp_municipal["sgp_total_asignado_2027"] = sgp_municipal[component_columns].sum(axis=1)
    sgp_municipal["poblacion_proyectada_2027"] = pd.to_numeric(
        sgp_municipal["POBLACIÓN 2027"], errors="coerce"
    )
    sgp_municipal["alerta_sgp_2027"] = sgp_municipal["Alerta"]
    sgp_municipal = sgp_municipal.rename(columns={"Nombre": "municipio_fuente"})

    if sgp_municipal["divipola"].duplicated().any():
        raise ValueError("Duplicados DIVIPOLA en la fuente municipal SGP.")
    result = universe.merge(
        sgp_municipal[["divipola", "municipio_fuente", "poblacion_proyectada_2027", "alerta_sgp_2027",
                       *component_columns, "sgp_total_asignado_2027"]],
        on="divipola", how="left", validate="one_to_one"
    )
    result.insert(2, "municipio_homologado", result["municipio"])
    result["anio"] = 2027
    result["unidad_monetaria"] = "pesos corrientes colombianos"
    result["magnitud"] = "asignacion/proyeccion SGP; no ejecucion"
    result["fuente_principal"] = "DNP/SGP, hoja SGP_2027_SGP"
    result = result[["divipola", "municipio", "municipio_homologado", "municipio_fuente", "departamento", "anio",
                     "poblacion_proyectada_2027", "alerta_sgp_2027", *component_columns,
                     "sgp_total_asignado_2027", "unidad_monetaria", "magnitud", "fuente_principal"]]

    missing_coverage = result["municipio_fuente"].isna().sum()
    if result["divipola"].duplicated().any() or len(result) != 31:
        raise ValueError("La base final no conserva una fila por municipio IOT.")
    if missing_coverage:
        raise ValueError("Hay municipios IOT sin asignación SGP homologada.")
    if (result[component_columns + ["sgp_total_asignado_2027"]] < 0).any().any():
        raise ValueError("Se encontraron asignaciones monetarias negativas.")
    logger.info("Validación territorial aprobada: 31 municipios y 31 DIVIPOLA únicos")

    output = PROCESSED / "dataset_09_inversion_publica_infraestructura.csv"
    result.to_csv(output, index=False, encoding="utf-8")

    coverage = []
    for column in result.columns:
        non_null = int(result[column].notna().sum())
        coverage.append({"dataset": "09", "variable": column, "filas_total": len(result),
                         "no_nulos": non_null, "nulos": len(result) - non_null,
                         "cobertura_pct": round(non_null / len(result) * 100, 2),
                         "anio_referencia": 2027 if column.startswith("sgp_") or column in {"poblacion_proyectada_2027", "alerta_sgp_2027"} else pd.NA})
    pd.DataFrame(coverage).to_csv(PROCESSED / "cobertura_09.csv", index=False, encoding="utf-8")

    audit_records = [
        {"dataset": "09", "etapa": "inventario", "severidad": "info", "hallazgo": "Fuente SGP municipal disponible; SECOP disponible solo a nivel departamental/contrato.", "tratamiento": "Usar SGP para la base municipal; no territorializar SECOP.", "estado": "resuelto"},
        {"dataset": "09", "etapa": "territorio", "severidad": "info", "hallazgo": "32 registros SGP con código 27; 27000 corresponde al agregado departamental.", "tratamiento": "Excluir 27000 de la salida municipal y conservarlo como control de inventario.", "estado": "resuelto"},
        {"dataset": "09", "etapa": "territorio", "severidad": "info", "hallazgo": "Los 31 DIVIPOLA del universo IOT están presentes una vez en SGP 2027.", "tratamiento": "Unión uno a uno por DIVIPOLA; se conserva nombre fuente y nombre homologado.", "estado": "resuelto"},
        {"dataset": "09", "etapa": "monetaria", "severidad": "media", "hallazgo": "Los valores SGP son proyecciones/asignaciones 2027 en pesos corrientes, no gasto ejecutado.", "tratamiento": "Mantener magnitud y unidad explícitas; no deflactar ni comparar temporalmente.", "estado": "requiere_revision_humana"},
        {"dataset": "09", "etapa": "infraestructura", "severidad": "media", "hallazgo": "No hay fuente municipal de proyectos/obras (PIIP) ni SGR/SICODIS incorporada.", "tratamiento": "No inferir infraestructura física ni inversión por obra desde SGP.", "estado": "bloqueo_externo"},
        {"dataset": "09", "etapa": "secop", "severidad": "media", "hallazgo": "SECOP_Gob_Choco tiene 9,186 contratos; Ciudad y Departamento están 'No Definido'.", "tratamiento": "No agregar valores contractuales a municipio; conservar la limitación documental.", "estado": "bloqueo_externo"},
    ]
    for path in raw_files:
        audit_records.append({"dataset": "09", "etapa": "inventario", "severidad": "info",
                              "hallazgo": f"RAW inventariado: {path.name} ({path.suffix}, {path.stat().st_size} bytes).",
                              "tratamiento": "Conservado sin modificación en RAW.", "estado": "registrado"})
    audit = pd.DataFrame(audit_records)
    audit.to_csv(PROCESSED / "auditoria_09.csv", index=False, encoding="utf-8")

    methodology = pd.DataFrame([{
        "dataset": "09", "objetivo": "Base municipal trazable de asignaciones/proyecciones SGP 2027 para el universo IOT Chocó; no mide ejecución ni infraestructura física existente.",
        "universo": "31 municipios IOT Chocó, definido por dataset_01_poblacion_territorio_choco_definitivo.csv", "unidad_original": "Municipio × concepto SGP (hoja SGP_2027_SGP); contrato para SECOP", "unidad_final": "municipio (una fila) con componentes SGP 2027", "clave_territorial": "DIVIPOLA (divipola, texto de cinco dígitos)",
        "fuentes": f"{SOURCE_09.name}: SGP_2027_SGP, SECOP_Gob_Choco, Inventario_fuentes, Diccionario y Metodologia; {UNIVERSE.name} para universo territorial.",
        "variables": "Componentes originales SGP 2027, población proyectada, alerta y sgp_total_asignado_2027 (suma de 13 componentes monetarios).", "transformaciones": "Lectura con header=2; DIVIPOLA estandarizado a cinco dígitos; filtro códigos 27; exclusión documentada de 27000 agregado departamental; unión uno a uno por DIVIPOLA; nombres de fuente preservados.",
        "tratamiento_nulos": "No se reemplazaron NA por cero. Los componentes SGP municipales no contienen nulos; cobertura calculada por variable.", "tratamiento_duplicados": "Se verificó unicidad de DIVIPOLA en universo, SGP municipal y salida. No se eliminaron duplicados municipales.", "homologacion_territorial": "DIVIPOLA fue la llave. municipio_fuente se conserva desde SGP; municipio y municipio_homologado provienen del universo IOT.",
        "agregacion": "No se agregaron proyectos ni contratos. sgp_total_asignado_2027 suma los 13 componentes monetarios por municipio; no incluye población ni alerta.", "limitaciones": "Solo una vigencia (2027) y valores corrientes. SGP representa asignación/proyección, no ejecución. SECOP no tiene localización municipal confiable.", "bloqueos": "Faltan PIIP municipal/proyecto y SGR/SICODIS municipal. Para incorporarlos se requiere archivo RAW con DIVIPOLA o una tabla territorial verificable.", "fecha_procesamiento": PROCESS_DATE
    }])
    methodology.to_csv(PROCESSED / "metodologia_09.csv", index=False, encoding="utf-8")
    logger.info("Archivos generados en %s", PROCESSED)
    logger.info("Resultado: %s filas, %s columnas, %s DIVIPOLA únicos", len(result), len(result.columns), result.divipola.nunique())
    logger.info("BLOQUEO EXTERNO: faltan PIIP y SGR/SICODIS municipales; SECOP no es territorializable")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise
