"""Construye el Dataset 10 como catálogo trazable de evidencia cualitativa.

No agrega ni puntúa evidencia cualitativa. Las referencias municipales son
menciones textuales literales en el campo territorio, no medidas municipales.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from datetime import date
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EPISODE = next(ROOT.joinpath("episodios").glob("002_EL_*"))
DATA = EPISODE / "Data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
LOG_DIR = EPISODE / "logs"
SOURCE = next(RAW.glob("dataset_10_historia_evidencia_cualitativa_*.xlsx"))
UNIVERSE = RAW / "dataset_01_poblacion_territorio_choco_definitivo.csv"


def normalized(value: object) -> str:
    text = unicodedata.normalize("NFD", str(value)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def logger_setup() -> logging.Logger:
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger("dataset_10")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(LOG_DIR / "dataset_10.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    return logger


def literal_municipality_mentions(text: object, universe: pd.DataFrame) -> pd.DataFrame:
    """Returns municipality names that equal a complete territory-text segment.

    Semicolon and slash delimiters are the only supported separators in the RAW.
    This deliberately avoids substring matches such as "Atrato" inside "Bajo Atrato".
    """
    segments = {normalized(segment) for segment in re.split(r"[;/]", str(text))}
    matches = []
    for row in universe.itertuples(index=False):
        name = normalized(row.municipio)
        if name in segments:
            matches.append({"divipola": row.divipola, "municipio": row.municipio})
    return pd.DataFrame(matches)


def main() -> None:
    logger = logger_setup()
    PROCESSED.mkdir(exist_ok=True)
    logger.info("Inicio Dataset 10")
    for path in sorted(item for item in RAW.iterdir() if item.is_file()):
        logger.info("Inventario RAW | archivo=%s | extension=%s | bytes=%s | modificado=%s",
                    path.name, path.suffix, path.stat().st_size,
                    date.fromtimestamp(path.stat().st_mtime).isoformat())

    universe = pd.read_csv(UNIVERSE, dtype={"divipola": "string"})[["divipola", "municipio"]].copy()
    universe["divipola"] = universe["divipola"].str.zfill(5)
    if len(universe) != 31 or universe.divipola.duplicated().any():
        raise ValueError("El universo IOT debe contener 31 DIVIPOLA únicos.")

    workbook = pd.ExcelFile(SOURCE)
    logger.info("Archivo fuente=%s | hojas=%s", SOURCE.name, ", ".join(workbook.sheet_names))
    sheets = {sheet: pd.read_excel(workbook, sheet_name=sheet) for sheet in workbook.sheet_names}
    for sheet, frame in sheets.items():
        logger.info("Hoja inspeccionada | hoja=%s | filas=%s | columnas=%s | campos=%s",
                    sheet, len(frame), len(frame.columns), list(frame.columns))

    library = sheets["Biblioteca"].copy()
    sources = sheets["Fuentes"].copy()
    cases = sheets["Casos"].copy()
    concepts = sheets["Conceptos"].copy()
    methodology_source = sheets["Metodologia"].copy()

    if library.id.duplicated().any() or sources.id.duplicated().any():
        raise ValueError("IDs duplicados en Biblioteca o Fuentes.")
    if set(library.id) != set(sources.id):
        raise ValueError("Biblioteca y Fuentes no contienen el mismo conjunto de IDs.")
    if not set(cases.fuente).issubset(set(library.id)):
        raise ValueError("Hay casos que apuntan a una fuente ausente de Biblioteca.")
    library = library.merge(sources[["id", "institucion"]], on="id", how="left", validate="one_to_one")
    if library.institucion.isna().any():
        raise ValueError("Falta institución para al menos un registro de Biblioteca.")

    records = []
    mention_rows = []
    for row in library.itertuples(index=False):
        mentions = literal_municipality_mentions(row.territorio, universe)
        names = "; ".join(mentions.municipio.tolist()) if not mentions.empty else pd.NA
        codes = "; ".join(mentions.divipola.tolist()) if not mentions.empty else pd.NA
        # Sólo se rellena la clave principal cuando la propia fila menciona un municipio IOT único.
        unique = mentions.iloc[0] if len(mentions) == 1 else None
        record = row._asdict()
        record.update({
            "divipola": unique.divipola if unique is not None else pd.NA,
            "municipio": unique.municipio if unique is not None else pd.NA,
            "municipio_homologado": unique.municipio if unique is not None else pd.NA,
            "municipio_fuente": row.territorio,
            "municipios_iot_mencionados": names,
            "divipola_iot_mencionados": codes,
            "nivel_observacion": "documento/investigacion/caso cualitativo",
            "tipo_territorio_fuente": "municipal_unico" if len(mentions) == 1 else ("multimunicipal" if len(mentions) > 1 else "supramunicipal_o_no_homologable"),
        })
        records.append(record)
        for mention in mentions.itertuples(index=False):
            mention_rows.append({"id": row.id, "divipola": mention.divipola, "municipio": mention.municipio})

    final = pd.DataFrame(records)
    final = final[["id", "divipola", "municipio", "municipio_homologado", "municipio_fuente",
                   "municipios_iot_mencionados", "divipola_iot_mencionados", "tipo_territorio_fuente",
                   "categoria", "autor", "institucion", "año", "titulo", "tipo", "territorio", "tema", "metodologia",
                   "hallazgo", "uso", "calidad", "enlace", "nota", "nivel_observacion"]]
    final = final.rename(columns={"año": "anio_publicacion", "tipo": "tipo_documento", "metodologia": "metodologia_fuente"})
    if final.id.duplicated().any() or len(final) != len(library):
        raise ValueError("La salida debe preservar una fila por documento fuente.")

    mention_table = pd.DataFrame(mention_rows).drop_duplicates()
    municipalities_mentioned = mention_table.divipola.nunique() if not mention_table.empty else 0
    municipality_unique_records = final.divipola.notna().sum()
    logger.info("Unidad confirmada: documento/investigacion/caso; no municipio-año")
    logger.info("Cobertura: %s de 31 municipios IOT mencionados literalmente; %s registros con municipio único",
                municipalities_mentioned, municipality_unique_records)

    final.to_csv(PROCESSED / "dataset_10_historia_evidencia_cualitativa_choco.csv", index=False, encoding="utf-8")

    coverage = pd.DataFrame([
        {"dataset": "10", "medida": "municipios_universo_iot", "valor": 31, "denominador": 31, "porcentaje": 100.0,
         "nota": "Universo de referencia Dataset 01."},
        {"dataset": "10", "medida": "municipios_mencionados_literalmente", "valor": municipalities_mentioned, "denominador": 31,
         "porcentaje": round(municipalities_mentioned / 31 * 100, 2), "nota": "Mención en texto territorial; no equivale a cobertura de un indicador municipal."},
        {"dataset": "10", "medida": "municipios_sin_mencion_literal", "valor": 31 - municipalities_mentioned, "denominador": 31,
         "porcentaje": round((31 - municipalities_mentioned) / 31 * 100, 2), "nota": "Sin registro/mención en esta biblioteca, no cero ni ausencia de fenómeno."},
        {"dataset": "10", "medida": "registros_documentales", "valor": len(final), "denominador": len(final), "porcentaje": 100.0,
         "nota": "Unidad final: documento/investigación/caso."},
        {"dataset": "10", "medida": "registros_fuera_universo_o_supramunicipales", "valor": int(final.divipola.isna().sum()), "denominador": len(final),
         "porcentaje": round(final.divipola.isna().mean() * 100, 2), "nota": "No homologables a un único municipio sin inferencia."},
    ])
    coverage.to_csv(PROCESSED / "cobertura_10.csv", index=False, encoding="utf-8")

    audit = pd.DataFrame([
        {"dataset": "10", "etapa": "integridad", "severidad": "info", "hallazgo": "7 IDs en Biblioteca y Fuentes; conjuntos de IDs coinciden.", "tratamiento": "Conservar una fila por documento y URL fuente.", "estado": "resuelto"},
        {"dataset": "10", "etapa": "unidad", "severidad": "info", "hallazgo": "La unidad de observación es documento, investigación o caso cualitativo.", "tratamiento": "No agregar, cuantificar ni convertir a un indicador municipal.", "estado": "resuelto"},
        {"dataset": "10", "etapa": "territorio", "severidad": "media", "hallazgo": f"{municipalities_mentioned} municipios IOT aparecen como menciones textuales; sólo {municipality_unique_records} registros tienen una mención municipal única.", "tratamiento": "Conservar territorio original y mención literal; DIVIPOLA principal sólo para referencia municipal única.", "estado": "resuelto"},
        {"dataset": "10", "etapa": "territorio", "severidad": "media", "hallazgo": "Hay alcances Chocó, Pacífico afrocolombiano, Bajo Atrato, multirregión y múltiples municipios.", "tratamiento": "No hacer matching difuso, no desagregar ni generalizar evidencia.", "estado": "requiere_revision_humana"},
        {"dataset": "10", "etapa": "variables", "severidad": "info", "hallazgo": "Categorías, calidad, hallazgos y notas son textuales/descriptivas.", "tratamiento": "Conservar categorías originales; sin codificación ordinal o numérica.", "estado": "resuelto"},
        {"dataset": "10", "etapa": "bloqueo_externo", "severidad": "media", "hallazgo": "No existe una fuente RAW que permita convertir la biblioteca cualitativa en medición municipal comparable.", "tratamiento": "Cerrar como catálogo documental; requerir fuente municipal estructurada sólo si se desea un indicador cuantitativo.", "estado": "bloqueo_externo"},
    ])
    audit.to_csv(PROCESSED / "auditoria_10.csv", index=False, encoding="utf-8")

    methodology = pd.DataFrame([{
        "dataset": "10", "objetivo": "Catálogo reproducible de evidencia cualitativa para contextualizar y orientar investigación; no un indicador IOT.",
        "universo_iot_referencia": "31 municipios del Dataset 01", "unidad_original": "Documento, investigación o caso", "unidad_final": "Una fila por registro de Biblioteca", "clave_territorial": "DIVIPOLA sólo cuando territorio menciona literalmente un único municipio IOT; de otro modo se conserva texto original.",
        "fuentes": f"{SOURCE.name}, hojas Biblioteca, Conceptos, Casos, Fuentes y Metodologia; {UNIVERSE.name} para contraste territorial.",
        "variables": "Metadatos bibliográficos, alcance territorial, tema, metodología de fuente, hallazgo, uso, calidad, enlace, nota y trazabilidad territorial.",
        "transformaciones": "año→anio_publicacion; tipo→tipo_documento; metodologia→metodologia_fuente; normalización de texto exclusivamente para buscar menciones literales de municipios; se conservan valores originales.",
        "tratamiento_nulos": "No se imputan valores. DIVIPOLA/municipio quedan NA cuando no hay una mención municipal única y literal.",
        "homologacion_territorial": "Se compara territorio contra nombres normalizados del universo; no matching difuso. Las menciones múltiples permanecen como lista y no se convierten en filas municipales.",
        "agregacion": "No hay agregación: la evidencia cualitativa no se convierte automáticamente en medida o indicador.",
        "limitaciones": "Cobertura documental parcial, alcances territoriales heterogéneos y ausencia de mediciones municipio-año.",
        "bloqueos": "Para construir un indicador municipal cuantitativo se requeriría una fuente RAW estructurada por municipio o una codificación metodológica aprobada.",
        "fecha_procesamiento": date.today().isoformat(),
    }])
    methodology.to_csv(PROCESSED / "metodologia_10.csv", index=False, encoding="utf-8")
    logger.info("Salida generada: %s filas, %s columnas, %s IDs únicos, %s nulos DIVIPOLA intencionales",
                len(final), len(final.columns), final.id.nunique(), final.divipola.isna().sum())
    logger.info("Resultado cerrado con limitaciones: catálogo cualitativo no municipal")


if __name__ == "__main__":
    main()
