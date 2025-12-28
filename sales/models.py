from django.db import models
from inventory.models import Product, Market

class Sale(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    sell_price = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)

    sold_at = models.DateTimeField(auto_now_add=True)