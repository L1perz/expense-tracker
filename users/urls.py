from django.urls import path

from ledger import views as edit_views
from . import views

app_name = "users"
urlpatterns = [
    path("", views.user_list, name="list"),
    path("new/", edit_views.edit, {"kind": "user"}, name="create"),
    path("<int:pk>/edit/", edit_views.edit, {"kind": "user"}, name="edit"),
    path("<int:pk>/delete/", edit_views.delete, {"kind": "user"}, name="delete"),
]
