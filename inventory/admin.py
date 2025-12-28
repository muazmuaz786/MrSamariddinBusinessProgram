from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from .models import Market, Product, Location
from sales.models import Sale

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ["name"]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "location", "stock", "sold", "purchase_price", "sell_price"]
    list_filter = ["location"]
    search_fields = ["name"]

class MarketAdminForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text="if you want to change the password, enter a new one here."
    )

    class Meta:
        model = Market
        fields = ["name"]

    def save(self, commit=True):
        obj = super().save(commit=False)
        pwd = self.cleaned_data.get("password")
        if pwd:
            obj.password_hash = make_password(pwd)
        if commit:
            obj.save()
        return obj
    
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Market

    
@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ("name",)

    def save_model(self, request, obj, form, change):
        if not obj.password_hash.startswith("pbkdf2_"):
            obj.password_hash = make_password(obj.password_hash)
        super().save_model(request, obj, form, change)