"""Punto de entrada para consolidar archivos departamentales validados."""

from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
INTERIM_DIR = PROJECT_DIR / "data" / "interim"


def main() -> None:
    """Prepara rutas e informa las condiciones previas a consolidar."""
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    archivos = [
        path
        for path in RAW_DIR.rglob("*")
        if path.is_file() and path.name not in {".gitkeep", "README.md"}
    ]

    print("ETAPA 03 — CONSOLIDACIÓN")
    print(f"Archivos fuente disponibles: {len(archivos)}")
    print(f"Directorio intermedio: {INTERIM_DIR}")
    print("Pendiente: consolidar solo después de validar estructura y codificación comunes.")


if __name__ == "__main__":
    main()