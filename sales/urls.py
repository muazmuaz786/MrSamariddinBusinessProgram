from django.urls import path
from . import views

urlpatterns = [
    path("sell/<int:pk>/", views.sell_page, name="sell_page"),   # GET
    path("sell/<int:pk>/do/", views.sell_product, name="sell_product"),  # POST
]
