"""Integracion territorial de las dimensiones del episodio."""

from pathlib import Path


EPISODIO_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = EPISODIO_DIR / "data" / "processed"
OUTPUTS_DIR = EPISODIO_DIR / "outputs" / "tables"



def main() -> None:
    """Prepara la integracion y enumera los insumos analiticos."""

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    insumos = sorted(PROCESSED_DIR.glob("*"))
    print("ETAPA 05 — INTEGRACION")
    print(f"Datasets procesados encontrados: {len(insumos)}")
    print(f"Salidas de validacion: {OUTPUTS_DIR}")
    print("Pendiente: integrar por DIVIPOLA y verificar duplicados, faltantes y periodos.")


if __name__ == "__main__":
    main()
