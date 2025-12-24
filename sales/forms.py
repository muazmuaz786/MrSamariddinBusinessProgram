from django import forms

class SellForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)
