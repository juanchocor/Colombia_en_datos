from pathlib import Path

# Root directory of the repository
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Episode directory
EPISODE_DIR = PROJECT_ROOT / "episodios" / "001_embarazo_adolescente"

# Data directories
RAW_DATA_DIR = EPISODE_DIR / "data" / "raw"
INTERIM_DATA_DIR = EPISODE_DIR / "data" / "interim"
PROCESSED_DATA_DIR = EPISODE_DIR / "data" / "processed"

# Output directory
OUTPUTS_DIR = EPISODE_DIR / "outputs"