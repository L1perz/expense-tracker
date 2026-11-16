"""Запуск консольного интерфейса с общей базой Django."""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_tracker.settings")
django.setup()

from ledger.console import main  # noqa: E402

if __name__ == "__main__":
    main()
