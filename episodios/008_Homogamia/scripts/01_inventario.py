"""Inventario local de nombres y tamaños de archivos fuente."""

import csv
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
OUTPUT_FILE = PROJECT_DIR / "outputs" / "tables" / "inventario_archivos.csv"


def main() -> None:
    """Lista archivos en raw sin abrir ni leer su contenido."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    archivos = sorted(
        path
        for path in RAW_DIR.rglob("*")
        if path.is_file() and path.name not in {".gitkeep", "README.md"}
    )

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as archivo_salida:
        campos = ["ruta_relativa", "extension", "tamano_bytes"]
        escritor = csv.DictWriter(archivo_salida, fieldnames=campos)
        escritor.writeheader()

        for ruta in archivos:
            escritor.writerow(
                {
                    "ruta_relativa": ruta.relative_to(RAW_DIR).as_posix(),
                    "extension": ruta.suffix.lower(),
                    "tamano_bytes": ruta.stat().st_size,
                }
            )

    print(f"Archivos inventariados: {len(archivos)}")
    print(f"Inventario guardado en: {OUTPUT_FILE}")
    print("El script solo registra rutas y tamaños; no lee los microdatos.")


if __name__ == "__main__":
    main()