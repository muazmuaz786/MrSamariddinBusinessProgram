from django.db import models

class Market(models.Model):
    name = models.CharField(max_length=100)
    password_hash = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Location(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
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
            .filter(product=self, market=self.market)
            .aggregate(x=Sum(profit_expr))["x"]
            or 0
        )

class Debt(models.Model):
    market = models.ForeignKey("Market", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)

    customer_name = models.CharField(max_length=100)

    quantity = models.PositiveIntegerField()
    returned = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def remaining(self):
        return self.quantity - self.returned

    def __str__(self):
        return f"{self.customer_name} - {self.product.name}"
