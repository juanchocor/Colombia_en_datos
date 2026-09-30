"""Integra cobertura de acueducto con la geometria municipal de 2018."""

from pathlib import Path

import geopandas as gpd
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
EPISODIO_DIR = SCRIPT_DIR.parent
PROCESSED_DIR = EPISODIO_DIR / "data" / "processed"
RAW_DIR = EPISODIO_DIR / "data" / "raw"

COBERTURA_FILE = PROCESSED_DIR / "cobertura_acueducto_2018_procesada.csv"
GEOMETRIA_FILE = RAW_DIR / "geometria_municipal_2018.geojson"
OUTPUT_FILE = PROCESSED_DIR / "acueducto_2018_integrado.geojson"

EXPECTED_MUNICIPIOS = 1122


def estandarizar_codigo(serie: pd.Series) -> pd.Series:
	"""Convierte codigos territoriales a texto de cinco digitos."""

	return (
		serie.astype("string")
		.str.strip()
		.str.replace(r"\.0$", "", regex=True)
		.str.zfill(5)
	)


def validar_fuente(nombre: str, datos: pd.DataFrame, clave: str) -> set[str]:
	"""Valida nulos y unicidad de la clave territorial."""

	if clave not in datos.columns:
		raise KeyError(f"La fuente {nombre} no contiene la columna {clave}.")

	nulos = int(datos[clave].isna().sum())
	duplicados = int(datos[clave].duplicated().sum())

	if nulos or duplicados:
		raise ValueError(
			f"{nombre}: clave {clave} invalida; "
			f"nulos={nulos}, duplicados={duplicados}."
		)

	return set(datos[clave])


def main() -> None:
	"""Carga, valida, integra y guarda la base espacial."""

	if not COBERTURA_FILE.exists():
		raise FileNotFoundError(f"No existe el CSV: {COBERTURA_FILE}")
	if not GEOMETRIA_FILE.exists():
		raise FileNotFoundError(f"No existe el GeoJSON: {GEOMETRIA_FILE}")

	cobertura = pd.read_csv(
		COBERTURA_FILE,
		dtype={"MPIO_CCDGO": "string"},
	)
	geometria = gpd.read_file(GEOMETRIA_FILE)

	cobertura["MPIO_CCDGO"] = estandarizar_codigo(cobertura["MPIO_CCDGO"])
	geometria["MPIO_CDPMP"] = estandarizar_codigo(geometria["MPIO_CDPMP"])

	claves_cobertura = validar_fuente(
		"cobertura de acueducto",
		cobertura,
		"MPIO_CCDGO",
	)
	claves_geometria = validar_fuente(
		"geometria municipal",
		geometria,
		"MPIO_CDPMP",
	)

	sin_geometria = sorted(claves_cobertura - claves_geometria)
	sin_cobertura = sorted(claves_geometria - claves_cobertura)

	print("--- VALIDACION DE MUNICIPIOS ---")
	print(f"Municipios geometria: {len(claves_geometria)}")
	print(f"Municipios acueducto: {len(claves_cobertura)}")
	print(f"Sin geometria: {len(sin_geometria)}")
	print(f"Sin informacion de acueducto: {len(sin_cobertura)}")

	if sin_geometria:
		print(f"Codigos de acueducto sin geometria: {sin_geometria}")
	if sin_cobertura:
		print(f"Codigos de geometria sin acueducto: {sin_cobertura}")

	if (
		len(claves_cobertura) != EXPECTED_MUNICIPIOS
		or len(claves_geometria) != EXPECTED_MUNICIPIOS
		or sin_geometria
		or sin_cobertura
	):
		raise ValueError(
			"La validacion territorial no cumple: se esperaban "
			f"{EXPECTED_MUNICIPIOS} municipios coincidentes."
		)

	cobertura = cobertura.rename(columns={"MPIO_CCDGO": "codigo_municipio"})
	geometria = geometria.rename(columns={"MPIO_CDPMP": "codigo_municipio"})

	integrada = geometria.merge(
		cobertura,
		on="codigo_municipio",
		how="left",
		validate="one_to_one",
		indicator=True,
	)

	sin_match = int((integrada["_merge"] != "both").sum())
	municipios_integrados = int(integrada["codigo_municipio"].nunique())
	columnas_cobertura = [
		"viviendas_con_acueducto",
		"viviendas_sin_acueducto",
		"viviendas_total",
		"cobertura_acueducto_pct",
		"sin_cobertura_pct",
	]
	sin_informacion = integrada[
		integrada[columnas_cobertura].isna().any(axis=1)
	]

	print(f"Municipios integrados: {municipios_integrados}")
	print(f"Sin coincidencia: {sin_match}")
	print(f"Municipios sin informacion de cobertura: {len(sin_informacion)}")

	if not sin_informacion.empty:
		print(
			sin_informacion[
				["codigo_municipio", "MPIO_CNMBR"]
				+ columnas_cobertura
			].to_string(index=False)
		)

	if (
		sin_match
		or municipios_integrados != EXPECTED_MUNICIPIOS
		or not sin_informacion.empty
	):
		raise ValueError(
			"La integracion territorial tiene coincidencias, pero no esta "
			"completa por datos faltantes de cobertura."
		)

	integrada = integrada.drop(columns=["_merge"])
	integrada.to_file(OUTPUT_FILE, driver="GeoJSON", index=False)

	print("\nBase espacial integrada guardada en:")
	print(OUTPUT_FILE)


if __name__ == "__main__":
	main()
