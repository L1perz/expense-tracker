from django.apps import AppConfig
from django.db.backends.signals import connection_created


class LedgerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ledger"
    verbose_name = "Личные финансы"

    def ready(self):
        from .db_functions import register_sqlite_functions

        connection_created.connect(
            register_sqlite_functions, dispatch_uid="ledger.sqlite_unicode_casefold"
        )
