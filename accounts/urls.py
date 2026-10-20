from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("", views.account_list, name="list"),
    path("<int:account_id>/", views.account_detail, name="detail"),
]
