from django.contrib import admin
from .models import Sale

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ["product", "quantity", "sold_at"]
    search_fields = ["product__name"]
