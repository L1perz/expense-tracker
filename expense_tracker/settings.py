"""Конфигурация Django 5.2 с прямым подключением к SQLite."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-expense-tracker-local-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]",
).split(",")

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "homepage.apps.HomepageConfig",
    "accounts.apps.AccountsConfig",
    "operations.apps.OperationsConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "homepage.middleware.DatabaseStatusMiddleware",
]
ROOT_URLCONF = "expense_tracker.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
    ]},
}]
WSGI_APPLICATION = "expense_tracker.wsgi.application"
ASGI_APPLICATION = "expense_tracker.asgi.application"
DATABASES = {}  # Данные приложения доступны через sqlite3 без Django ORM.
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DATA_DIR = Path(os.environ.get("EXPENSE_DATA_DIR", BASE_DIR / "data"))
EXPENSE_DB_PATH = Path(os.environ.get("EXPENSE_DB_PATH", DATA_DIR / "expenses.sqlite"))
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
