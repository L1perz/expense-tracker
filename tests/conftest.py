"""Django Client без ORM и плагина pytest-django."""

import os

import django
import pytest
from django.test import Client, override_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_tracker.settings")
django.setup()


@pytest.fixture
def client():
    with override_settings(ALLOWED_HOSTS=["testserver"], DEBUG=False):
        yield Client()
