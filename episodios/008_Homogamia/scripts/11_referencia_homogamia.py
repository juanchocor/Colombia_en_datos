
from pathlib import Path
import pandas as pd


# ============================================================
# 1. RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

ARCHIVO_PERSONAS = (
    BASE_DIR
    / "data"
    / "interim"
    / "personas_medellin.csv"
)

ARCHIVO_PAREJAS = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "parejas_identificadas_medellin.csv"
)

DIR_SALIDA = BASE_DIR / "outputs" / "tables"
DIR_SALIDA.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. CATEGORÍAS
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

# Para la comparación principal excluimos "No informa".
CODIGOS_VALIDOS = ["1", "2", "3", "4", "5", "6"]

ORDEN = [ETNIAS[c] for c in CODIGOS_VALIDOS]


def limpiar_codigo(serie):
    return (
        serie.astype("string")
        .str.strip()
        .replace({
            "": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
            "NA": pd.NA,
        })
    )


def etiquetar(serie):
    return serie.map(ETNIAS).fillna("Sin dato/código no reconocido")


# ============================================================
# 3. DISTRIBUCIÓN ÉTNICA DE LA POBLACIÓN
# ============================================================

print("Leyendo categoría étnica de la población...")

personas = pd.read_csv(
    ARCHIVO_PERSONAS,
    usecols=["PA1_GRP_ETNIC"],
    dtype=str,
    encoding="utf-8-sig"
)

personas["etnia"] = limpiar_codigo(personas["PA1_GRP_ETNIC"])

total_personas = len(personas)

conteo_poblacion = (
    personas.loc[
        personas["etnia"].isin(CODIGOS_VALIDOS),
        "etnia"
    ]
    .value_counts()
    .reindex(CODIGOS_VALIDOS, fill_value=0)
)

total_poblacion_valida = int(conteo_poblacion.sum())

distribucion_poblacion = pd.DataFrame({
    "codigo_etnico": CODIGOS_VALIDOS,
    "categoria_etnica": ORDEN,
    "personas": conteo_poblacion.values,
})

distribucion_poblacion["porcentaje"] = (
    distribucion_poblacion["personas"]
    / total_poblacion_valida
    * 100
).round(4)

proporciones_poblacion = (
    conteo_poblacion / total_poblacion_valida
)

print(f"Personas en archivo: {total_personas:,}")
print(f"Con categoría válida (1-6): {total_poblacion_valida:,}")


# ============================================================
# 4. PAREJAS OBSERVADAS
# ============================================================

print("\nLeyendo parejas identificadas...")

parejas = pd.read_csv(
    ARCHIVO_PAREJAS,
    usecols=[
        "jefe_PA1_GRP_ETNIC",
        "pareja_PA1_GRP_ETNIC",
    ],
    dtype=str,
    encoding="utf-8-sig"
)

parejas["etnia_jefatura"] = limpiar_codigo(
    parejas["jefe_PA1_GRP_ETNIC"]
)

parejas["etnia_pareja"] = limpiar_codigo(
    parejas["pareja_PA1_GRP_ETNIC"]
)

# La comparación principal incluye solo parejas en las que
# ambos integrantes tienen una categoría válida entre 1 y 6.
parejas_validas = parejas.loc[
    parejas["etnia_jefatura"].isin(CODIGOS_VALIDOS)
    & parejas["etnia_pareja"].isin(CODIGOS_VALIDOS)
].copy()

parejas_validas["jefatura"] = etiquetar(
    parejas_validas["etnia_jefatura"]
)

parejas_validas["pareja"] = etiquetar(
    parejas_validas["etnia_pareja"]
)

n_parejas = len(parejas_validas)

observada = pd.crosstab(
    parejas_validas["jefatura"],
    parejas_validas["pareja"]
).reindex(
    index=ORDEN,
    columns=ORDEN,
    fill_value=0
)

print(f"Parejas en archivo: {len(parejas):,}")
print(f"Parejas con ambas categorías válidas: {n_parejas:,}")


# ============================================================
# 5. REFERENCIA A: COMPOSICIÓN DE LA POBLACIÓN
# ============================================================

# Para cada categoría de jefatura, distribuimos sus parejas
# según la proporción de cada categoría en la población censal.
#
# Es un escenario de referencia, NO una predicción de parejas
# reales ni una estimación causal de preferencias.

totales_jefatura = observada.sum(axis=1)

esperada_poblacion = pd.DataFrame(
    {
        categoria: (
            totales_jefatura
            * proporciones_poblacion[codigo]
        )
        for codigo, categoria in zip(CODIGOS_VALIDOS, ORDEN)
    },
    index=ORDEN
)

esperada_poblacion = esperada_poblacion.reindex(
    index=ORDEN,
    columns=ORDEN
)


# ============================================================
# 6. REFERENCIA B: EMPAREJAMIENTO ALEATORIO
# ============================================================

# Conserva la distribución observada de las categorías entre
# jefaturas y entre parejas, pero supone independencia entre
# las categorías de ambos integrantes.
#
# Esperado(i,j) = total_fila(i) * total_columna(j) / N

totales_parejas_por_categoria = observada.sum(axis=0)

esperada_aleatoria = pd.DataFrame(
    index=ORDEN,
    columns=ORDEN,
    dtype=float
)

for categoria_jefatura in ORDEN:
    for categoria_pareja in ORDEN:
        esperada_aleatoria.loc[
            categoria_jefatura, categoria_pareja
        ] = (
            totales_jefatura[categoria_jefatura]
            * totales_parejas_por_categoria[categoria_pareja]
            / n_parejas
        )


# ============================================================
# 7. COMPARACIÓN DE COINCIDENCIAS
# ============================================================

coincidencia_observada = int(
    sum(
        observada.loc[categoria, categoria]
        for categoria in ORDEN
    )
)

coincidencia_esperada_poblacion = float(
    sum(
        esperada_poblacion.loc[categoria, categoria]
        for categoria in ORDEN
    )
)

coincidencia_esperada_aleatoria = float(
    sum(
        esperada_aleatoria.loc[categoria, categoria]
        for categoria in ORDEN
    )
)

porcentaje_observado = (
    coincidencia_observada / n_parejas * 100
    if n_parejas else 0
)

porcentaje_esperado_poblacion = (
    coincidencia_esperada_poblacion / n_parejas * 100
    if n_parejas else 0
)

porcentaje_esperado_aleatorio = (
    coincidencia_esperada_aleatoria / n_parejas * 100
    if n_parejas else 0
)

resumen = pd.DataFrame([
    {
        "escenario": "Coincidencia observada",
        "parejas_coincidentes": coincidencia_observada,
        "porcentaje": porcentaje_observado,
    },
    {
        "escenario": "Referencia: composición poblacional",
        "parejas_coincidentes": coincidencia_esperada_poblacion,
        "porcentaje": porcentaje_esperado_poblacion,
    },
    {
        "escenario": "Referencia: emparejamiento aleatorio",
        "parejas_coincidentes": coincidencia_esperada_aleatoria,
        "porcentaje": porcentaje_esperado_aleatorio,
    },
])

resumen["parejas_coincidentes"] = (
    resumen["parejas_coincidentes"].round(2)
)

resumen["porcentaje"] = resumen["porcentaje"].round(4)


# ============================================================
# 8. DIFERENCIA ENTRE OBSERVADO Y ESPERADO
# ============================================================

diferencia_poblacion = (
    observada - esperada_poblacion
).round(2)

diferencia_aleatoria = (
    observada - esperada_aleatoria
).round(2)


# ============================================================
# 9. EXPORTAR
# ============================================================

salidas = {
    "distribucion_etnica_poblacion_medellin.csv":
        distribucion_poblacion,

    "matriz_observada_homogamia_medellin.csv":
        observada,

    "matriz_esperada_composicion_poblacional.csv":
        esperada_poblacion,

    "diferencia_observada_vs_poblacion.csv":
        diferencia_poblacion,

    "matriz_esperada_emparejamiento_aleatorio.csv":
        esperada_aleatoria,

    "diferencia_observada_vs_aleatoria.csv":
        diferencia_aleatoria,

    "comparacion_coincidencia_homogamia.csv":
        resumen,
}

for nombre, tabla in salidas.items():
    tabla.to_csv(
        DIR_SALIDA / nombre,
        encoding="utf-8-sig"
    )


# ============================================================
# 10. RESULTADOS EN CONSOLA
# ============================================================

print("\n========== DISTRIBUCIÓN DE LA POBLACIÓN ==========")
print(distribucion_poblacion.to_string(index=False))

print("\n========== MATRIZ OBSERVADA ==========")
print(observada.to_string())

print("\n========== ESPERADO: COMPOSICIÓN POBLACIONAL ==========")
print(esperada_poblacion.round(2).to_string())

print("\n========== ESPERADO: EMPAREJAMIENTO ALEATORIO ==========")
print(esperada_aleatoria.round(2).to_string())

print("\n========== COMPARACIÓN DE COINCIDENCIAS ==========")
print(resumen.to_string(index=False))

print("\nArchivos generados:")
for nombre in salidas:
    print(f"- {DIR_SALIDA / nombre}")
