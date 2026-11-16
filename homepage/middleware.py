from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

from db.database import DatabaseNotReady
from django.db import OperationalError, ProgrammingError


class DatabaseStatusMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        missing_table = isinstance(
            exception, (OperationalError, ProgrammingError)
        ) and ("no such table" in str(exception).lower())
        if isinstance(exception, DatabaseNotReady) or missing_table:
            return render(request, "503.html", status=503)
        return None
