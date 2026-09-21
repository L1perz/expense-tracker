"""Чтение и запись JSON без перезаписи поврежденных данных."""

import json
from pathlib import Path

from .service import ExpenseTracker


class JsonStorage:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> ExpenseTracker:
        if not self.path.exists():
            return ExpenseTracker()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return ExpenseTracker.from_dict(data)
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            raise ValueError(f"Поврежден файл {self.path}: {error}") from error

    def save(self, tracker: ExpenseTracker) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(tracker.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.path)
