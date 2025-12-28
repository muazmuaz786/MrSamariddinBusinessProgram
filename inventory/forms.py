from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Product, Location

class ProductForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        market_id = kwargs.pop("market_id", None)
        super().__init__(*args, **kwargs)

        if market_id:
            self.fields["location"].queryset = Location.objects.filter(
                market_id=market_id
            )
        else:
            self.fields["location"].queryset = Location.objects.none()

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

class debtstockform(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        label=_("Miqdor"),
    )