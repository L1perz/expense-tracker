from django.urls import path

from . import views
from ledger import views as edit_views

app_name = "operations"
urlpatterns = [
    path("", views.operation_list, name="list"),
    path("statistics/", views.statistics, name="statistics"),
    path("new/", edit_views.edit, {"kind": "operation"}, name="create"),
    path("<int:pk>/edit/", edit_views.edit, {"kind": "operation"}, name="edit"),
    path("<int:operation_id>/cancel/", edit_views.cancel, name="cancel"),
    path("<int:operation_id>/", views.operation_detail, name="detail"),
]
