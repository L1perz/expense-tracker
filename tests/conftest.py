"""Django Client без ORM и плагина pytest-django."""

import os

import django
import pytest
from django.test import Client, override_settings

from db.database import BASE_DIR
from db.import_json import import_json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_tracker.settings")
django.setup()


@pytest.fixture
def client(tmp_path):
    database = tmp_path / "web.sqlite"
    import_json(BASE_DIR / "data", database)
    with override_settings(ALLOWED_HOSTS=["testserver"], DEBUG=False,
                           EXPENSE_DB_PATH=database):
        yield Client()
