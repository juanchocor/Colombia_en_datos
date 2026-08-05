"""Utilidades pequeñas compartidas."""

from pathlib import Path


def ensure_directory(path: Path) -> Path:
    """Crea un directorio si no existe y devuelve la ruta."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def normalize_column_name(name: str) -> str:
    """Normaliza nombres de columnas para facilitar merges y validaciones."""
    return name.strip().lower().replace(" ", "_")
