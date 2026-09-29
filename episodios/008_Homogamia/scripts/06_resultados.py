"""Punto de entrada para exportar tablas y resultados reproducibles."""

from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
FIGURES_DIR = PROJECT_DIR / "outputs" / "figures"
TABLES_DIR = PROJECT_DIR / "outputs" / "tables"


def main() -> None:
    """Prepara los directorios de salida del episodio."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    print("ETAPA 06 — RESULTADOS")
    print(f"Tablas: {TABLES_DIR}")
    print(f"Figuras: {FIGURES_DIR}")
    print("Pendiente: generar resultados después de validar emparejamientos e indicadores.")


if __name__ == "__main__":
    main()