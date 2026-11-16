"""Конфигурация Django 5.2 с прямым подключением к SQLite."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-expense-tracker-local-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS",
    "localhost,127.0.0.1,[::1]",
).split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "homepage.apps.HomepageConfig",
    "users.apps.UsersConfig",
    "categories.apps.CategoriesConfig",
    "accounts.apps.AccountsConfig",
    "operations.apps.OperationsConfig",
    "ledger.apps.LedgerConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "homepage.middleware.DatabaseStatusMiddleware",
]
ROOT_URLCONF = "expense_tracker.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "ledger.context_processors.site_info",
            ]
        },
    }
]
WSGI_APPLICATION = "expense_tracker.wsgi.application"
ASGI_APPLICATION = "expense_tracker.asgi.application"
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DATA_DIR = Path(os.environ.get("EXPENSE_DATA_DIR", BASE_DIR / "data"))
EXPENSE_DB_PATH = Path(os.environ.get("EXPENSE_DB_PATH", DATA_DIR / "expenses.sqlite"))
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DJANGO_DB_PATH", DATA_DIR / "ledger.sqlite3"),
        "OPTIONS": {"timeout": 10},
    }
}
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
INTERNAL_IPS = ["127.0.0.1", "::1"]
if DEBUG and os.environ.get("DJANGO_DEBUG_TOOLBAR") == "1":
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
