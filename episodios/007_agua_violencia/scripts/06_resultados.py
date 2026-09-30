"""Generacion de resultados descriptivos del episodio."""

from pathlib import Path


EPISODIO_DIR = Path(__file__).resolve().parents[1]
FIGURES_DIR = EPISODIO_DIR / "outputs" / "figures"
TABLES_DIR = EPISODIO_DIR / "outputs" / "tables"



def main() -> None:
    """Prepara las salidas finales del episodio."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    print("ETAPA 06 — RESULTADOS")
    print(f"Tablas: {TABLES_DIR}")
    print(f"Graficos: {FIGURES_DIR}")
    print("Pendiente: generar estadisticas descriptivas, mapas y exportaciones narrativas.")
    print("Recordatorio: las asociaciones espaciales no demuestran causalidad.")


if __name__ == "__main__":
    main()
