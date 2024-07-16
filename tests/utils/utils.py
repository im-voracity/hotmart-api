import os
import json
from pathlib import Path
from typing import Dict, Any


def get_project_root() -> Path:
    """
    Retorna o diretório raiz do projeto.
    """
    return Path(__file__).parent.parent.parent


def read_config() -> Dict[str, Any]:
    """
    Lê o arquivo config.json do diretório PROJECT_ROOT/secrets e retorna como um dicionário.

    Returns:
        Dict[str, Any]: O conteúdo do arquivo JSON como um dicionário.

    Raises:
        FileNotFoundError: Se o diretório ou o arquivo não existirem.
        json.JSONDecodeError: Se o arquivo não puder ser decodificado como JSON.
        KeyError: Se as chaves necessárias não existirem.
        ValueError: Se as chaves necessárias estiverem vazias.
    """
    project_root = get_project_root()
    secrets_dir = project_root / "secrets"
    config_file = secrets_dir / "config.json"

    if not secrets_dir.is_dir():
        raise FileNotFoundError(f"Directory {secrets_dir} does not exist.")

    if not config_file.is_file():
        raise FileNotFoundError(f"Config file {config_file} does not exist.")

    try:
        with config_file.open("r") as file:
            config = json.load(file)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Error decoding config file: {e}")

    required_keys = ["client_id", "client_secret", "basic"]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Required key '{key}' is missing from the config file.")
        if not config[key]:
            raise ValueError(f"Required key '{key}' has an empty value in the config file.")

    return config

