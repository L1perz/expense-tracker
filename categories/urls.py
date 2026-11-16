from django.urls import path

from ledger import views as edit_views
from . import views

app_name = "categories"
urlpatterns = [
    path("", views.category_list, name="list"),
    path("new/", edit_views.edit, {"kind": "category"}, name="create"),
    path("<int:pk>/edit/", edit_views.edit, {"kind": "category"}, name="edit"),
    path("<int:pk>/delete/", edit_views.delete, {"kind": "category"}, name="delete"),
]
