from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import set_language

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("inventory/", include("inventory.urls")),
    path("sales/", include("sales.urls")),
    path("analytics/", include("analytics.urls")),
    path("i18n/setlang/", set_language, name="set_language"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
