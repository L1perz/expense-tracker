from django.urls import path

from . import views
from ledger import views as edit_views

app_name = "homepage"
urlpatterns = [
    path("", views.index, name="index"),
    path("users/", views.user_list, name="users"),
    path("categories/", views.category_list, name="categories"),
    path("users/new/", edit_views.edit, {"kind": "user"}, name="user_create"),
    path("users/<int:pk>/edit/", edit_views.edit, {"kind": "user"}, name="user_edit"),
    path(
        "users/<int:pk>/delete/",
        edit_views.delete,
        {"kind": "user"},
        name="user_delete",
    ),
    path(
        "categories/new/", edit_views.edit, {"kind": "category"}, name="category_create"
    ),
    path(
        "categories/<int:pk>/edit/",
        edit_views.edit,
        {"kind": "category"},
        name="category_edit",
    ),
    path(
        "categories/<int:pk>/delete/",
        edit_views.delete,
        {"kind": "category"},
        name="category_delete",
    ),
]
