from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "image",
            "location",
            "purchase_price",
            "sell_price",
            "stock",
        ]
        labels = {
            "name": _("Mahsulot nomi"),
            "image": _("Rasm"),
            "location": _("Joylashuv"),
            "purchase_price": _("Sotib olish narxi"),
            "sell_price": _("Sotish narxi"),
            "stock": _("Zaxira"),
        }
