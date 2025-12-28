from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import set_language
from inventory.views import home

from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import include

urlpatterns = [
    path("", home, name="home"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("inventory/", include("inventory.urls")),
    path("sales/", include("sales.urls")),
    path("analytics/", include("analytics.urls")),
    path("admin/", admin.site.urls),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
