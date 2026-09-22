"""Загрузка и сохранение коллекций в JSON."""

import json
from pathlib import Path


def load_data(filename: Path) -> list[dict]:
    """Загрузить список словарей; при отсутствии файла вернуть пустой список."""
    try:
        with filename.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError(f"Некорректный JSON в файле {filename.name}.") from error
    if not isinstance(data, list):
        raise ValueError(f"В файле {filename.name} должен находиться список.")
    return data


def save_data(filename: Path, data: list[dict]) -> None:
    """Сохранить список словарей в JSON через контекстный менеджер."""
    filename.parent.mkdir(parents=True, exist_ok=True)
    with filename.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
