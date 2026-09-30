
from pathlib import Path
import pandas as pd

# ============================================================
# 1. RUTAS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "raw" / "censo_2018" / "antioquia"
OUTPUT_DIR = ROOT / "outputs" / "tables"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. LECTURA DE CSV
# ============================================================

def leer_csv(ruta):
    errores = []

    for encoding in ["utf-8", "utf-8-sig", "cp1252", "latin-1"]:
        try:
            df = pd.read_csv(
                ruta,
                sep=None,
                engine="python",
                encoding=encoding,
                nrows=5
            )

            if len(df.columns) == 1:
                errores.append(
                    f"{encoding}: solo se detectó una columna"
                )
                continue

            return df, encoding

        except Exception as error:
            errores.append(f"{encoding}: {error}")

    raise ValueError(
        f"No se pudo leer {ruta.name}:\n" +
        "\n".join(errores)
    )

# ============================================================
# 3. INVENTARIO DE UN ARCHIVO
# ============================================================

def inventariar(ruta):

    print(f"\n{'=' * 70}")
    print(f"LEYENDO: {ruta.name}")
    print("=" * 70)

    df, encoding = leer_csv(ruta)

    print(f"Codificación: {encoding}")
    print(f"Filas: {len(df):,}")
    print(f"Columnas: {len(df.columns):,}")
    print(f"Duplicados exactos: {df.duplicated().sum():,}")

    print("\nNombres de variables:")
    for columna in df.columns:
        print(f"  {columna}")

    print("\nMuestra de registros:")
    print(df.head(5).to_string(index=False))

    resumen = {
        "archivo": ruta.name,
        "tamano_mb": round(ruta.stat().st_size / 1024**2, 2),
        "filas": len(df),
        "columnas": len(df.columns),
        "codificacion": encoding,
        "duplicados_exactos": int(df.duplicated().sum()),
        "variables": " | ".join(map(str, df.columns)),
    }

    perfil = pd.DataFrame({
        "archivo": ruta.name,
        "variable": df.columns.astype(str),
        "tipo_dato": df.dtypes.astype(str).values,
        "valores_nulos": [
            int(df[col].isna().sum()) for col in df.columns
        ],
        "porcentaje_nulos": [
            round(df[col].isna().mean() * 100, 2)
            for col in df.columns
        ],
        "valores_unicos": [
            int(df[col].nunique(dropna=True))
            for col in df.columns
        ],
    })

    return resumen, perfil


# ============================================================
# 4. EJECUCIÓN
# ============================================================

def main():

    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"No existe la carpeta: {DATA_DIR}"
        )

    archivos = sorted(DATA_DIR.glob("*.csv"))

    if not archivos:
        raise FileNotFoundError(
            f"No se encontraron CSV en {DATA_DIR}"
        )

    resumenes = []
    perfiles = []
    errores = []

    print(f"Archivos encontrados: {len(archivos)}")
    print(f"Carpeta: {DATA_DIR}")

    for archivo in archivos:
        try:
            resumen, perfil = inventariar(archivo)
            resumenes.append(resumen)
            perfiles.append(perfil)

        except Exception as error:
            errores.append({
                "archivo": archivo.name,
                "error": str(error)
            })
            print(f"\nERROR: {archivo.name}")
            print(error)

    if resumenes:
        pd.DataFrame(resumenes).to_csv(
            OUTPUT_DIR / "inventario_archivos.csv",
            index=False,
            encoding="utf-8-sig"
        )

    if perfiles:
        pd.concat(perfiles, ignore_index=True).to_csv(
            OUTPUT_DIR / "perfil_variables.csv",
            index=False,
            encoding="utf-8-sig"
        )

    if errores:
        pd.DataFrame(errores).to_csv(
            OUTPUT_DIR / "errores_lectura.csv",
            index=False,
            encoding="utf-8-sig"
        )

    print("\n" + "=" * 70)
    print("INVENTARIO FINALIZADO")
    print(f"Archivos leídos: {len(resumenes)}")
    print(f"Archivos con errores: {len(errores)}")
    print(f"Resultados: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()