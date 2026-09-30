
from pathlib import Path
import pandas as pd


# ============================================================
# 1. RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

ARCHIVO_ENTRADA = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "parejas_identificadas_medellin.csv"
)

DIR_SALIDA = BASE_DIR / "outputs" / "tables"
DIR_SALIDA.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. CATEGORÍAS ÉTNICAS
# ============================================================

ETNIAS = {
    "1": "Indígena",
    "2": "Gitano/Rrom",
    "3": "Raizal",
    "4": "Palenquero de San Basilio",
    "5": "Negro/mulato/afrodescendiente/afrocolombiano",
    "6": "Ningún grupo étnico",
    "9": "No informa",
}

# Códigos que identifican un grupo étnico específico.
# El código 6 no se interpreta como una etnia.
GRUPOS_ETNICOS = {"1", "2", "3", "4", "5"}


# ============================================================
# 3. IDENTIFICAR LAS COLUMNAS
# ============================================================

def buscar_columna(columnas, rol):
    """
    Busca la columna PA1_GRP_ETNIC correspondiente al rol.
    Admite nombres con sufijos o prefijos como:
    PA1_GRP_ETNIC_jefe, J_PA1_GRP_ETNIC,
    PA1_GRP_ETNIC_pareja, etc.
    """

    objetivo = "PA1_GRP_ETNIC"
    candidatas = []

    for columna in columnas:
        nombre = columna.upper()

        if objetivo not in nombre:
            continue

        if rol == "jefatura":
            indicadores = ["JEFE", "JEFATURA"]
        else:
            indicadores = ["PAREJA", "CONYUGE", "CÓNYUGE"]

        if any(indicador in nombre for indicador in indicadores):
            candidatas.append(columna)

    if len(candidatas) == 1:
        return candidatas[0]

    if len(candidatas) == 0:
        raise ValueError(
            f"No encontré la columna étnica de {rol}.\n"
            f"Columnas disponibles:\n{list(columnas)}"
        )

    raise ValueError(
        f"Encontré varias columnas para {rol}: {candidatas}\n"
        "Define manualmente cuál utilizar."
    )


# ============================================================
# 4. CARGA DE DATOS
# ============================================================

print("Leyendo archivo de parejas...")

if not ARCHIVO_ENTRADA.exists():
    raise FileNotFoundError(
        f"No existe el archivo: {ARCHIVO_ENTRADA}"
    )

columnas = pd.read_csv(
    ARCHIVO_ENTRADA,
    nrows=0,
    encoding="utf-8-sig"
).columns

col_jefatura = buscar_columna(columnas, "jefatura")
col_pareja = buscar_columna(columnas, "pareja")

print(f"Columna étnica de jefatura: {col_jefatura}")
print(f"Columna étnica de pareja: {col_pareja}")

df = pd.read_csv(
    ARCHIVO_ENTRADA,
    usecols=[col_jefatura, col_pareja],
    dtype=str,
    encoding="utf-8-sig"
)

print(f"Parejas cargadas: {len(df):,}")


# ============================================================
# 5. LIMPIEZA Y ETIQUETAS
# ============================================================

def limpiar_codigo(serie):
    return (
        serie
        .astype("string")
        .str.strip()
        .replace({
            "": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
            "NA": pd.NA,
        })
    )


df["etnia_jefatura"] = limpiar_codigo(df[col_jefatura])
df["etnia_pareja"] = limpiar_codigo(df[col_pareja])

df["etnia_jefatura_nombre"] = (
    df["etnia_jefatura"].map(ETNIAS).fillna("Código desconocido")
)

df["etnia_pareja_nombre"] = (
    df["etnia_pareja"].map(ETNIAS).fillna("Código desconocido")
)


# ============================================================
# 6. MATRIZ DE CONTEOS
# ============================================================

ORDEN = list(ETNIAS.values())

matriz_conteos = pd.crosstab(
    df["etnia_jefatura_nombre"],
    df["etnia_pareja_nombre"],
    dropna=False
)

# Asegurar un orden estable de categorías
filas = [x for x in ORDEN if x in matriz_conteos.index]
columnas_ordenadas = [
    x for x in ORDEN if x in matriz_conteos.columns
]

matriz_conteos = matriz_conteos.reindex(
    index=filas,
    columns=columnas_ordenadas,
    fill_value=0
)

# Incluir posibles códigos desconocidos
if "Código desconocido" in df["etnia_jefatura_nombre"].values:
    if "Código desconocido" not in matriz_conteos.index:
        matriz_conteos.loc["Código desconocido"] = 0

if "Código desconocido" in df["etnia_pareja_nombre"].values:
    if "Código desconocido" not in matriz_conteos.columns:
        matriz_conteos["Código desconocido"] = 0


# ============================================================
# 7. PORCENTAJES POR FILA
# ============================================================

# Cada fila suma 100% cuando tiene observaciones.
# Indica cómo se distribuyen las categorías de las parejas
# dentro de cada categoría étnica de la jefatura.

matriz_porcentajes = (
    matriz_conteos
    .div(matriz_conteos.sum(axis=1).replace(0, pd.NA), axis=0)
    * 100
)

matriz_porcentajes = matriz_porcentajes.round(2)


# ============================================================
# 8. COINCIDENCIA DE CATEGORÍAS
# ============================================================

j = df["etnia_jefatura"]
p = df["etnia_pareja"]

# Coincidencia en la categoría censal reportada.
# Excluye los códigos desconocidos y "No informa".
informacion_reportada = (
    j.isin(set(ETNIAS) - {"9"})
    & p.isin(set(ETNIAS) - {"9"})
)

misma_categoria = (
    informacion_reportada & j.eq(p)
)

categorias_distintas = (
    informacion_reportada & j.ne(p)
)

# Coincidencia en un grupo étnico específico (códigos 1-5).
# Excluye "Ningún grupo étnico" y "No informa".
ambos_grupos_identificados = (
    j.isin(GRUPOS_ETNICOS)
    & p.isin(GRUPOS_ETNICOS)
)

mismo_grupo_etnico = (
    ambos_grupos_identificados & j.eq(p)
)

grupos_etnicos_distintos = (
    ambos_grupos_identificados & j.ne(p)
)

resumen = pd.DataFrame([
    {
        "indicador": "Total de parejas identificadas",
        "parejas": len(df),
    },
    {
        "indicador": "Ambos tienen categoría reportada (códigos 1-6)",
        "parejas": int(informacion_reportada.sum()),
    },
    {
        "indicador": "Misma categoría censal reportada (códigos 1-6)",
        "parejas": int(misma_categoria.sum()),
    },
    {
        "indicador": "Categorías censales distintas (códigos 1-6)",
        "parejas": int(categorias_distintas.sum()),
    },
    {
        "indicador": "Ambos reportan un grupo étnico específico (1-5)",
        "parejas": int(ambos_grupos_identificados.sum()),
    },
    {
        "indicador": "Mismo grupo étnico específico (1-5)",
        "parejas": int(mismo_grupo_etnico.sum()),
    },
    {
        "indicador": "Grupos étnicos específicos distintos (1-5)",
        "parejas": int(grupos_etnicos_distintos.sum()),
    },
    {
        "indicador": "Jefatura sin categoría étnica válida",
        "parejas": int((~j.isin(ETNIAS.keys())).sum()),
    },
    {
        "indicador": "Pareja sin categoría étnica válida",
        "parejas": int((~p.isin(ETNIAS.keys())).sum()),
    },
])


# ============================================================
# 9. EXPORTAR RESULTADOS
# ============================================================

archivo_conteos = (
    DIR_SALIDA / "matriz_etnica_parejas_medellin.csv"
)

archivo_porcentajes = (
    DIR_SALIDA / "matriz_etnica_porcentajes_medellin.csv"
)

archivo_resumen = (
    DIR_SALIDA / "resumen_homogamia_etnica_medellin.csv"
)

matriz_conteos.to_csv(
    archivo_conteos,
    encoding="utf-8-sig"
)

matriz_porcentajes.to_csv(
    archivo_porcentajes,
    encoding="utf-8-sig"
)

resumen.to_csv(
    archivo_resumen,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 10. RESULTADOS EN CONSOLA
# ============================================================

print("\n========== MATRIZ DE CONTEOS ==========")
print(matriz_conteos.to_string())

print("\n========== PORCENTAJES POR FILA ==========")
print(matriz_porcentajes.to_string())

print("\n========== RESUMEN ==========")
print(resumen.to_string(index=False))

print("\nArchivos generados:")
print(f"- {archivo_conteos}")
print(f"- {archivo_porcentajes}")
print(f"- {archivo_resumen}")