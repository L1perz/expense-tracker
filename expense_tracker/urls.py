from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("categories/", include("categories.urls")),
    path("", include("homepage.urls")),
    path("accounts/", include("accounts.urls")),
    path("operations/", include("operations.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
handler404 = "homepage.views.page_not_found"
