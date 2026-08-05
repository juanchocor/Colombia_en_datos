"""Configuracion general del proyecto."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EPISODES_DIR = PROJECT_ROOT / "episodios"
RAW_DATA_DIR = EPISODES_DIR / "001_embarazo_adolescente" / "data" / "raw"
DEFAULT_ENCODING = "utf-8"
