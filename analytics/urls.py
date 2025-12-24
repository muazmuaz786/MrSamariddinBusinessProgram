from django.urls import path
from .views import sales_analytics

urlpatterns = [
    path("", sales_analytics, name="sales_analytics"),
]
