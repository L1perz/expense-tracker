from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

from db.database import DatabaseNotReady


class DatabaseStatusMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, DatabaseNotReady):
            return render(request, "503.html", status=503)
        return None
