import json
import os
from pathlib import Path
from typing import Any, Dict


def get_project_root() -> Path:
    """
    Retorna o diretório raiz do projeto.
    """
    return Path(__file__).parent.parent.parent


def read_config() -> Dict[str, Any]:
    """
    Reads the config.json file from the PROJECT_ROOT/secrets directory and returns it as a dictionary.

    Returns:
        Dict[str, Any]: The content of the JSON file as a dictionary.

    Raises:
        FileNotFoundError: If the directory or file does not exist.
        json.JSONDecodeError: If the file cannot be decoded as JSON.
        KeyError: If the required keys do not exist.
        ValueError: If the required keys are empty.
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
            raise ValueError(
                f"Required key '{key}' has an empty value in the config file."
            )

    return config
