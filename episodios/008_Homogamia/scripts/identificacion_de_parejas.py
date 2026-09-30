from pathlib import Path
import pandas as pd

# ============================================================
# RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

ARCHIVO = (
    BASE_DIR
    / "data"
    / "interim"
    / "personas_medellin.csv"
)

INTERIM = BASE_DIR / "data" / "interim"
SALIDA = BASE_DIR / "outputs" / "tables"

INTERIM.mkdir(parents=True, exist_ok=True)
SALIDA.mkdir(parents=True, exist_ok=True)

ARCHIVO_CANDIDATOS = INTERIM / "candidatos_pareja_medellin.csv"
ARCHIVO_PAREJAS = SALIDA / "parejas_identificadas_medellin.csv"
ARCHIVO_HOGARES = SALIDA / "resumen_hogares_medellin.csv"
ARCHIVO_REPORTE = SALIDA / "reporte_identificacion_medellin.csv"

# ============================================================
# CONFIGURACIÓN
# ============================================================

CLAVE_HOGAR = [
    "U_DPTO",
    "U_MPIO",
    "UA_CLASE",
    "COD_ENCUESTAS",
    "U_VIVIENDA",
    "P_NROHOG",
]

COLUMNAS = CLAVE_HOGAR + [
    "P_NRO_PER",
    "P_SEXO",
    "P_EDADR",
    "P_PARENTESCOR",
    "PA1_GRP_ETNIC",
    "P_EST_CIVIL",
]

COLUMNAS_PERSONA = [
    "P_NRO_PER",
    "P_SEXO",
    "P_EDADR",
    "P_PARENTESCOR",
    "PA1_GRP_ETNIC",
    "P_EST_CIVIL",
]

# ============================================================
# 1. EXTRAER JEFATURAS Y PAREJAS POR BLOQUES
# ============================================================

print("Leyendo personas de Medellín por bloques...")

if ARCHIVO_CANDIDATOS.exists():
    ARCHIVO_CANDIDATOS.unlink()

primero = True
total_candidatos = 0
total_registros = 0

for bloque in pd.read_csv(
    ARCHIVO,
    usecols=COLUMNAS,
    dtype=str,
    encoding="utf-8",
    chunksize=100_000,
):
    total_registros += len(bloque)

    # Solo conservamos jefaturas y parejas declaradas
    candidatos = bloque[
        bloque["P_PARENTESCOR"].isin(["1", "2"])
        & bloque["P_NROHOG"].notna()
    ].copy()

    if not candidatos.empty:
        candidatos.to_csv(
            ARCHIVO_CANDIDATOS,
            mode="w" if primero else "a",
            header=primero,
            index=False,
            encoding="utf-8",
        )

        primero = False
        total_candidatos += len(candidatos)

    print(
        f"\rProcesados: {total_registros:,} | "
        f"Jefaturas/parejas: {total_candidatos:,}",
        end="",
    )

print("\nExtracción terminada.")
print(f"Registros candidatos: {total_candidatos:,}")

if total_candidatos == 0:
    raise SystemExit(
        "No se encontraron jefaturas ni parejas con los códigos definidos."
    )

# ============================================================
# 2. AGRUPAR POR HOGAR
# ============================================================

print("Agrupando candidatos por hogar...")

df = pd.read_csv(
    ARCHIVO_CANDIDATOS,
    dtype=str,
    encoding="utf-8",
)

# Conteos por hogar y tipo de parentesco
conteos = (
    df.assign(
        es_jefatura=df["P_PARENTESCOR"].eq("1").astype(int),
        es_pareja=df["P_PARENTESCOR"].eq("2").astype(int),
    )
    .groupby(CLAVE_HOGAR, dropna=False)
    .agg(
        n_jefaturas=("es_jefatura", "sum"),
        n_parejas=("es_pareja", "sum"),
    )
    .reset_index()
)

# Clasificar estructura del hogar
def clasificar_hogar(fila):
    jefes = fila["n_jefaturas"]
    parejas = fila["n_parejas"]

    if jefes == 1 and parejas == 1:
        return "Una jefatura y una pareja"
    if jefes == 1 and parejas == 0:
        return "Una jefatura sin pareja registrada"
    if jefes == 1 and parejas > 1:
        return "Una jefatura y varias parejas registradas"
    if jefes > 1:
        return "Varias jefaturas"
    return "Sin jefatura identificada"

conteos["estructura"] = conteos.apply(
    clasificar_hogar,
    axis=1,
)

conteos.to_csv(
    ARCHIVO_HOGARES,
    index=False,
    encoding="utf-8-sig",
)

# ============================================================
# 3. IDENTIFICAR PAREJAS CON UNA SOLA JEFATURA Y UNA PAREJA
# ============================================================

hogares_validos = conteos.loc[
    (conteos["n_jefaturas"] == 1)
    & (conteos["n_parejas"] == 1),
    CLAVE_HOGAR,
]

df_validos = df.merge(
    hogares_validos,
    on=CLAVE_HOGAR,
    how="inner",
)

jefaturas = (
    df_validos[df_validos["P_PARENTESCOR"] == "1"]
    [CLAVE_HOGAR + COLUMNAS_PERSONA]
    .rename(
        columns={
            col: f"jefe_{col}"
            for col in COLUMNAS_PERSONA
        }
    )
)

parejas = (
    df_validos[df_validos["P_PARENTESCOR"] == "2"]
    [CLAVE_HOGAR + COLUMNAS_PERSONA]
    .rename(
        columns={
            col: f"pareja_{col}"
            for col in COLUMNAS_PERSONA
        }
    )
)

resultado = jefaturas.merge(
    parejas,
    on=CLAVE_HOGAR,
    how="inner",
    validate="one_to_one",
)

resultado.to_csv(
    ARCHIVO_PAREJAS,
    index=False,
    encoding="utf-8-sig",
)

# ============================================================
# 4. REPORTE RESUMIDO
# ============================================================

resumen = (
    conteos["estructura"]
    .value_counts(dropna=False)
    .rename_axis("estructura")
    .reset_index(name="hogares")
)

resumen["porcentaje"] = (
    resumen["hogares"] / len(conteos) * 100
).round(2)

resumen.to_csv(
    ARCHIVO_REPORTE,
    index=False,
    encoding="utf-8-sig",
)

# ============================================================
# 5. RESULTADOS
# ============================================================

print("\n========== RESULTADOS ==========")
print(f"Hogares con jefatura o pareja: {len(conteos):,}")
print(f"Parejas identificadas: {len(resultado):,}")

print("\nEstructura de hogares:")
print(resumen.to_string(index=False))

print("\nArchivos generados:")
print(f"- {ARCHIVO_PAREJAS}")
print(f"- {ARCHIVO_HOGARES}")
print(f"- {ARCHIVO_REPORTE}")
print(f"- {ARCHIVO_CANDIDATOS}")