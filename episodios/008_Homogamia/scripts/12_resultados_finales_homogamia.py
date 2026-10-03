
from pathlib import Path
import pandas as pd
import numpy as np

try:
    from scipy.stats import chi2_contingency
except ImportError:
    chi2_contingency = None


# ============================================================
# 1. RUTAS Y CONFIGURACIÓN
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

ETNIAS = {
    "1": "Indígena",
    "2": "Gitano/Rrom",
    "3": "Raizal",
    "4": "Palenquero de San Basilio",
    "5": "Negro/mulato/afrodescendiente/afrocolombiano",
    "6": "Ningún grupo étnico",
}

CODIGOS = list(ETNIAS.keys())
NOMBRES = list(ETNIAS.values())


# ============================================================
# 2. CARGA Y LIMPIEZA
# ============================================================

print("Leyendo parejas...")

df = pd.read_csv(
    ARCHIVO_ENTRADA,
    usecols=[
        "jefe_PA1_GRP_ETNIC",
        "pareja_PA1_GRP_ETNIC",
    ],
    dtype=str,
    encoding="utf-8-sig",
)

def limpiar(serie):
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

df["jefatura"] = limpiar(df["jefe_PA1_GRP_ETNIC"])
df["pareja"] = limpiar(df["pareja_PA1_GRP_ETNIC"])

# Se excluyen "No informa", faltantes y códigos no reconocidos.
df = df.loc[
    df["jefatura"].isin(CODIGOS)
    & df["pareja"].isin(CODIGOS)
].copy()

df["jefatura_nombre"] = df["jefatura"].map(ETNIAS)
df["pareja_nombre"] = df["pareja"].map(ETNIAS)

print(f"Parejas válidas: {len(df):,}")


# ============================================================
# 3. MATRIZ OBSERVADA
# ============================================================

observada = pd.crosstab(
    df["jefatura_nombre"],
    df["pareja_nombre"],
).reindex(
    index=NOMBRES,
    columns=NOMBRES,
    fill_value=0,
)

n = int(observada.to_numpy().sum())

totales_fila = observada.sum(axis=1)
totales_columna = observada.sum(axis=0)

# Bajo independencia, la probabilidad de que la pareja
# pertenezca a una categoría es su proporción entre las
# parejas observadas.
proporciones_pareja = totales_columna / n

esperada = pd.DataFrame(
    index=NOMBRES,
    columns=NOMBRES,
    dtype=float,
)

for categoria_j in NOMBRES:
    for categoria_p in NOMBRES:
        esperada.loc[categoria_j, categoria_p] = (
            totales_fila[categoria_j]
            * proporciones_pareja[categoria_p]
        )


# ============================================================
# 4. COINCIDENCIA POR CATEGORÍA DE LA JEFATURA
# ============================================================

filas_resultado = []

for categoria in NOMBRES:
    total = int(totales_fila[categoria])

    observado_diag = int(
        observada.loc[categoria, categoria]
    )

    esperado_diag = float(
        esperada.loc[categoria, categoria]
    )

    porcentaje_observado = (
        observado_diag / total * 100
        if total > 0 else np.nan
    )

    porcentaje_esperado = (
        esperado_diag / total * 100
        if total > 0 else np.nan
    )

    diferencia_pp = (
        porcentaje_observado - porcentaje_esperado
        if total > 0 else np.nan
    )

    razon_obs_esp = (
        observado_diag / esperado_diag
        if esperado_diag > 0 else np.nan
    )

    filas_resultado.append({
        "categoria_jefatura": categoria,
        "total_parejas": total,
        "coincidencias_observadas": observado_diag,
        "coincidencias_esperadas": round(esperado_diag, 2),
        "porcentaje_observado": round(
            porcentaje_observado, 2
        ),
        "porcentaje_esperado": round(
            porcentaje_esperado, 2
        ),
        "diferencia_puntos_porcentuales": round(
            diferencia_pp, 2
        ),
        "razon_observado_esperado": round(
            razon_obs_esp, 3
        ),
    })

por_categoria = pd.DataFrame(filas_resultado)


# ============================================================
# 5. COINCIDENCIA GLOBAL
# ============================================================

coincidencias_observadas = int(
    np.trace(observada.to_numpy())
)

coincidencias_esperadas = float(
    np.trace(esperada.to_numpy())
)

porcentaje_observado_global = (
    coincidencias_observadas / n * 100
)

porcentaje_esperado_global = (
    coincidencias_esperadas / n * 100
)

resumen_global = pd.DataFrame([{
    "parejas_validas": n,
    "coincidencias_observadas": coincidencias_observadas,
    "coincidencias_esperadas": round(
        coincidencias_esperadas, 2
    ),
    "porcentaje_observado": round(
        porcentaje_observado_global, 4
    ),
    "porcentaje_esperado": round(
        porcentaje_esperado_global, 4
    ),
    "diferencia_puntos_porcentuales": round(
        porcentaje_observado_global
        - porcentaje_esperado_global, 4
    ),
}])


# ============================================================
# 6. ASOCIACIÓN GLOBAL
# ============================================================

resultado_asociacion = {
    "parejas_validas": n,
    "chi2": np.nan,
    "grados_libertad": np.nan,
    "p_valor": np.nan,
    "cramers_v": np.nan,
    "celdas_esperadas_menores_5": np.nan,
    "celdas_esperadas_menores_1": np.nan,
    "nota": "",
}

if chi2_contingency is not None:
    chi2, p_valor, gl, esperados_test = chi2_contingency(
        observada.to_numpy(),
        correction=False,
    )

    filas, columnas = observada.shape
    cramers_v = np.sqrt(
        chi2 / (n * min(filas - 1, columnas - 1))
    )

    resultado_asociacion.update({
        "chi2": chi2,
        "grados_libertad": gl,
        "p_valor": p_valor,
        "cramers_v": cramers_v,
        "celdas_esperadas_menores_5": int(
            (esperados_test < 5).sum()
        ),
        "celdas_esperadas_menores_1": int(
            (esperados_test < 1).sum()
        ),
        "nota": (
            "Revisar celdas esperadas pequeñas. "
            "El valor p asintótico puede no ser fiable "
            "si muchas celdas tienen frecuencias esperadas bajas."
        ),
    })
else:
    resultado_asociacion["nota"] = (
        "SciPy no está instalado. Instalar con: "
        "pip install scipy"
    )

asociacion = pd.DataFrame([resultado_asociacion])


# ============================================================
# 7. EXPORTAR TABLAS
# ============================================================

salidas = {
    "homogamia_matriz_observada_final.csv": observada,
    "homogamia_matriz_esperada_final.csv": esperada.round(2),
    "homogamia_resultados_por_categoria.csv": por_categoria,
    "homogamia_resumen_global.csv": resumen_global,
    "homogamia_asociacion_estadistica.csv": asociacion,
}

for nombre, tabla in salidas.items():
    tabla.to_csv(
        DIR_SALIDA / nombre,
        encoding="utf-8-sig",
    )


# ============================================================
# 8. CONSOLA
# ============================================================

print("\n========== RESULTADOS POR CATEGORÍA ==========")
print(por_categoria.to_string(index=False))

print("\n========== RESUMEN GLOBAL ==========")
print(resumen_global.to_string(index=False))

print("\n========== ASOCIACIÓN GLOBAL ==========")
print(asociacion.to_string(index=False))

print("\n========== MATRIZ OBSERVADA ==========")
print(observada.to_string())

print("\nArchivos generados:")
for nombre in salidas:
    print(f"- {DIR_SALIDA / nombre}")
