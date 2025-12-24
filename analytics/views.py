from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import now
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from sales.models import Sale


@login_required
def sales_analytics(request):
    t = now()
    y, m = t.year, t.month
    d = t.date()

    revenue_expr = ExpressionWrapper(
        F("quantity") * F("sell_price"),
        output_field=DecimalField(max_digits=20, decimal_places=2)
    )

    profit_expr = ExpressionWrapper(
        F("quantity") * (F("sell_price") - F("purchase_price")),
        output_field=DecimalField(max_digits=20, decimal_places=2)
    )

    top_sales = (
        Sale.objects
        .values("product__name")
        .annotate(total=Sum("quantity"))
        .order_by("-total")[:5]
    )

    top_sales_labels = [x["product__name"] for x in top_sales]
    top_sales_values = [x["total"] for x in top_sales]
    
    product_stats = (
        Sale.objects
        .values("product__name")
        .annotate(
            revenue=Sum(
                F("quantity") * F("sell_price"),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            ),
            profit=Sum(
                F("quantity") * (F("sell_price") - F("purchase_price")),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            ),
        )
        .order_by("-revenue")[:10]
    )

    product_labels = [x["product__name"] for x in product_stats]
    product_revenue = [float(x["revenue"]) for x in product_stats]
    product_profit = [float(x["profit"]) for x in product_stats]

    top_profit_qs = (
        Sale.objects
        .values("product__name")
        .annotate(
            total_profit=Sum(
                F("quantity") * (F("sell_price") - F("purchase_price")),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        )
        .order_by("-total_profit")[:10]
    )

    top_profit_labels = [x["product__name"] for x in top_profit_qs]
    top_profit_values = [float(x["total_profit"] or 0) for x in top_profit_qs]

    pie_qs = (
        Sale.objects
        .values("product__name")
        .annotate(total=Sum("quantity"))
        .order_by("-total")[:5]
    )

    pie_labels = [x["product__name"] for x in pie_qs]
    pie_values = [int(x["total"] or 0) for x in pie_qs]

    def agg(qs):
        a = qs.aggregate(
            revenue=Sum(revenue_expr),
            profit=Sum(profit_expr),
            sold=Sum("quantity")
        )
        return {
            "revenue": a["revenue"] or 0,
            "profit": a["profit"] or 0,
            "sold": a["sold"] or 0,
        }

    today = agg(Sale.objects.filter(sold_at__date=d))
    month = agg(Sale.objects.filter(sold_at__year=y, sold_at__month=m))
    year  = agg(Sale.objects.filter(sold_at__year=y))

    return render(request, "analytics/sales_analytics.html", {
        "today": today,
        "month": month,
        "year": year,
        "top_sales_labels": top_sales_labels,
        "top_sales_values": top_sales_values,
        "product_labels": product_labels,
        "product_revenue": product_revenue,
        "product_profit": product_profit,
        "top_profit_labels": top_profit_labels,
        "top_profit_values": top_profit_values,
        "pie_labels": pie_labels,
        "pie_values": pie_values,
    })


