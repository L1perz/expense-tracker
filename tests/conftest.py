"""Django Client без ORM и плагина pytest-django."""

import os

import django
import pytest
from django.core.management import call_command


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_tracker.settings")
django.setup()


@pytest.fixture
def client(db, client, settings):
    settings.ALLOWED_HOSTS = ["testserver"]
    settings.DEBUG = False
    call_command("import_legacy", verbosity=0)
    return client
