"""Punto de entrada para identificar parejas convivientes."""

from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"


def main() -> None:
    """Prepara la etapa sin anticipar reglas de emparejamiento."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("ETAPA 04 — IDENTIFICACIÓN DE PAREJAS")
    print(f"Directorio de trabajo: {PROCESSED_DIR}")
    print("Pendiente: documentar claves, parentesco, sexo y controles de unicidad.")


if __name__ == "__main__":
    main()