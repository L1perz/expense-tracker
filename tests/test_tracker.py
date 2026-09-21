"""Проверки расчетов, сохранения и основных пользовательских сценариев."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest.mock import patch

from expense_tracker.cli import run
from expense_tracker.models import Budget, Expense, Transaction, parse_money
from expense_tracker.service import ExpenseTracker
from expense_tracker.storage import JsonStorage


class TrackerTests(unittest.TestCase):
    def test_money_and_invalid_input(self):
        self.assertEqual(parse_money("750,50"), 75050)
        self.assertEqual(parse_money("0.1") + parse_money("0.2"), 30)
        for value in ("abc", "", "-1", "NaN", "Infinity", "0.001"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_money(value)

    def test_crud_filters_and_totals(self):
        tracker = ExpenseTracker()
        first = tracker.add(250000, date(2026, 9, 1), "Закупка", "Продукты")
        second = tracker.add(75050, date(2026, 9, 22), "Проезд", "Транспорт")
        tracker.add(100, date(2026, 10, 1), "Хлеб", "Продукты")
        self.assertEqual(tracker.total("2026-09"), 325050)
        self.assertEqual(tracker.list_expenses("2026-09", "ТРАНСПОРТ"), [second])
        tracker.update(first.id, 10000, date(2026, 9, 1), "Еда", "Продукты")
        self.assertEqual(tracker.by_category("2026-09")["продукты"], 10000)
        tracker.delete(second.id)
        self.assertEqual(tracker.total("2026-09"), 10000)
        with self.assertRaises(ValueError):
            tracker.delete(999)

    def test_budget_boundaries(self):
        budget = Budget("2026-09", 100000)
        self.assertEqual(budget.remaining(90000), 10000)
        self.assertIn("полностью", budget.status(100000))
        self.assertIn("превышен", budget.status(100001))
        with self.assertRaises(ValueError):
            Budget("2026-13", 100)

    def test_oop_and_validation(self):
        expense = Expense(1, 100, date(2026, 9, 1), "Хлеб", "Продукты")
        self.assertIsInstance(expense, Transaction)
        self.assertIn("Продукты", expense.summary())
        with self.assertRaises(AttributeError):
            expense.amount = -1
        with self.assertRaises(ValueError):
            Expense(2, 0, date.today(), "Хлеб", "Продукты")

    def test_save_reload_and_id_not_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = JsonStorage(Path(directory) / "expenses.json")
            tracker = storage.load()
            tracker.add(100, date.today(), "Хлеб", "Продукты")
            tracker.set_budget("2026-09", 100000)
            tracker.delete(1)
            storage.save(tracker)
            restored = storage.load()
            expense = restored.add(200, date.today(), "Еда", "Продукты")
            self.assertEqual(expense.id, 2)
            self.assertEqual(restored.get_budget("2026-09").limit, 100000)

    def test_corrupt_file_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "expenses.json"
            path.write_text("broken", encoding="utf-8")
            with redirect_stdout(io.StringIO()) as output:
                run(path)
            self.assertIn("Не удалось загрузить", output.getvalue())
            self.assertEqual(path.read_text(encoding="utf-8"), "broken")

    def test_cli_and_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "expenses.json"
            inputs = ["5", "2026-09", "1000", "1", "250,50", "2026-09-22",
                      "Еда", "Обед", "6", "2026-09", "0"]
            with patch("builtins.input", side_effect=inputs):
                with redirect_stdout(io.StringIO()) as output:
                    run(path)
            self.assertIn("749.50 руб.", output.getvalue())
            with patch("builtins.input", side_effect=["2", "", "", "0"]):
                with redirect_stdout(io.StringIO()) as output:
                    run(path)
            self.assertIn("Обед", output.getvalue())

    def test_failed_save_does_not_apply_change(self):
        with tempfile.TemporaryDirectory() as directory:
            inputs = ["1", "100", "2026-09-22", "Еда", "Обед",
                      "2", "", "", "0"]
            with patch("builtins.input", side_effect=inputs):
                with patch.object(JsonStorage, "save", side_effect=OSError("Нет доступа")):
                    with redirect_stdout(io.StringIO()) as output:
                        run(Path(directory) / "expenses.json")
            self.assertIn("Изменения не сохранены", output.getvalue())
            self.assertIn("Расходов не найдено", output.getvalue())


if __name__ == "__main__":
    unittest.main()
