from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)

    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    sell_price = models.DecimalField(max_digits=12, decimal_places=2)

    stock = models.PositiveIntegerField(default=0)
    sold = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.name
    
    @property
    def unit_profit(self):
        return self.sell_price - self.purchase_price

    @property
    def total_profit(self):
        from sales.models import Sale
        from django.db.models import Sum, F, DecimalField, ExpressionWrapper

        profit_expr = ExpressionWrapper(
            F("quantity") * (F("sell_price") - F("purchase_price")),
            output_field=DecimalField(max_digits=20, decimal_places=2),
        )

        return (
            Sale.objects
            .filter(product=self)
            .aggregate(x=Sum(profit_expr))["x"]
            or 0
        )
