"""Unicode casefold для поиска в SQLite без дополнительных расширений."""

from django.db.models import Func


class UnicodeCasefold(Func):
    function = "UNICODE_CASEFOLD"
    arity = 1


def casefold(value):
    return value.casefold() if value is not None else None


def register_sqlite_functions(sender, connection, **kwargs):
    if connection.vendor == "sqlite":
        connection.connection.create_function(
            "UNICODE_CASEFOLD", 1, casefold, deterministic=True
        )
