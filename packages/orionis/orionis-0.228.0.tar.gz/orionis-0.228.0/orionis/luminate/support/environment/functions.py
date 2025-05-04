import ast
import os
from pathlib import Path
from typing import Any

def _initialize() -> Path:
    """
    Inicializa la ruta al archivo `.env`.
    """
    resolved_path = Path(os.getcwd()) / ".env"

    # Asegurarse de que el archivo .env exista
    if not resolved_path.exists():
        resolved_path.touch()

    return resolved_path

def _parse_value(value: Any) -> Any:
    """
    Parsea un valor de cadena en un tipo de dato de Python.
    """
    value = str(value).strip() if value is not None else None

    if not value or value.lower() in {'none', 'null'}:
        return None
    if value.lower() in {'true', 'false'}:
        return value.lower() == 'true'
    if value.isdigit():
        return int(value)
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value

def _serialize_value(value: Any) -> str:
    """
    Serializa un tipo de dato de Python en una cadena para almacenarlo en el archivo `.env`.
    """
    if isinstance(value, (list, dict, bool, int, float)):
        return repr(value)
    return str(value)

def _delete_file() -> None:
    """
    Elimina el archivo especificado.
    """
    resolved_path = Path(os.getcwd()) / ".env"
    if resolved_path.exists():
        os.remove(resolved_path)