from django.urls import path
from . import views

urlpatterns = [
    path("", views.inventory_list, name="inventory_list"),
    path("add/", views.product_add, name="product_add"),
    path("<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("<int:pk>/delete/force/", views.product_delete_force, name="product_delete_force"),
    path("debts/", views.debt_list, name="debt_list"),
    path("debts/add/", views.debt_create, name="debt_create"),
    path("debts/pay/<int:pk>/", views.debt_pay, name="debt_pay"),
    path("debts/delete/<int:pk>/", views.debt_delete, name="debt_delete"),
]
