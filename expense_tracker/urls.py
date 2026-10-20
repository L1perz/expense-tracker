from django.urls import include, path

urlpatterns = [
    path("", include("homepage.urls")),
    path("accounts/", include("accounts.urls")),
    path("operations/", include("operations.urls")),
]
handler404 = "homepage.views.page_not_found"
