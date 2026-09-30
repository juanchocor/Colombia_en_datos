"""Preparacion de la dimension de calidad o riesgo del agua."""

from pathlib import Path


EPISODIO_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = EPISODIO_DIR / "data" / "raw"
INTERIM_DIR = EPISODIO_DIR / "data" / "interim"
PROCESSED_DIR = EPISODIO_DIR / "data" / "processed"



def main() -> None:
    """Prepara rutas y verifica el insumo de calidad."""

    for directory in [RAW_DIR, INTERIM_DIR, PROCESSED_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    candidatos = list(RAW_DIR.glob("*"))
    print("ETAPA 03 — CALIDAD O RIESGO DEL AGUA")
    print(f"Insumos locales encontrados: {len(candidatos)}")
    print(f"Intermedios: {INTERIM_DIR}")
    print(f"Procesados: {PROCESSED_DIR}")
    print("Pendiente: confirmar el indicador oficial y no llamarlo agua potable sin respaldo metodologico.")


if __name__ == "__main__":
    main()
