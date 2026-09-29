"""Punto de entrada para calcular indicadores de homogamia étnica."""

from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"


def main() -> None:
    """Prepara la etapa y recuerda fijar universos y denominadores."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("ETAPA 05 — INDICADORES")
    print(f"Directorio de datos procesados: {PROCESSED_DIR}")
    print("Pendiente: fijar categorías étnicas, universo y denominador de cada indicador.")


if __name__ == "__main__":
    main()