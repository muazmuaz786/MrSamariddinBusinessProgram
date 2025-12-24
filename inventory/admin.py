from django.contrib import admin
from .models import Product, Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ["name"]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "location", "stock", "sold", "purchase_price", "sell_price"]
    list_filter = ["location"]
    search_fields = ["name"]
