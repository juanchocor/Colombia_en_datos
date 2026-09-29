"""Punto de entrada para validar archivos, variables y claves censales."""

from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"


def main() -> None:
    """Muestra insumos disponibles sin asumir todavía un formato."""
    archivos = sorted(
        path
        for path in RAW_DIR.rglob("*")
        if path.is_file() and path.name not in {".gitkeep", "README.md"}
    )

    print("ETAPA 02 — VALIDACIÓN")
    print(f"Archivos fuente encontrados: {len(archivos)}")
    print("Pendiente: confirmar formatos, diccionarios, identificadores y codificaciones.")


if __name__ == "__main__":
    main()