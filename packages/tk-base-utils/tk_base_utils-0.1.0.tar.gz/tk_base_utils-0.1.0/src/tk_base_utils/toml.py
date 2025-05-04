import tomllib

from pathlib import Path

from .file import  get_target_file_path

def load_toml(toml_file_path: Path|None = None,
              encoding: str = "utf-8"):
    if toml_file_path is None:
        toml_file_path = get_target_file_path("config.toml")
    with open(toml_file_path, "rb") as f:
        return tomllib.load(f)
    