"""Точка входа системы учета расходов."""
from pathlib import Path
from expense_tracker.cli import run

if __name__ == "__main__":
    run(Path(__file__).resolve().parent / "data" / "expenses.json")
