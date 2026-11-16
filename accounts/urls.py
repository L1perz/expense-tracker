from django.urls import path

from . import views
from ledger import views as edit_views

app_name = "accounts"
urlpatterns = [
    path("", views.account_list, name="list"),
    path("new/", edit_views.edit, {"kind": "account"}, name="create"),
    path("<int:pk>/edit/", edit_views.edit, {"kind": "account"}, name="edit"),
    path("<int:pk>/delete/", edit_views.delete, {"kind": "account"}, name="delete"),
    path("<int:account_id>/", views.account_detail, name="detail"),
    path("by-name/<slug:slug>/", views.account_detail, name="detail_slug"),
]
