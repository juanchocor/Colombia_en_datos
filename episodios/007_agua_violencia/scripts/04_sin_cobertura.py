"""Construccion de la dimension de ausencia de cobertura."""

from pathlib import Path


EPISODIO_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = EPISODIO_DIR / "data" / "processed"



def main() -> None:
    """Prepara la etapa de ausencia de cobertura."""

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("ETAPA 04 — SIN COBERTURA")
    print(f"Directorio de trabajo: {PROCESSED_DIR}")
    print("Pendiente: construir la variable solo cuando el denominador y la definicion oficial sean comparables.")


if __name__ == "__main__":
    main()
