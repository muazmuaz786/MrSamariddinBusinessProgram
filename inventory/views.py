from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F, DecimalField, ExpressionWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from inventory.models import Product, Location
from inventory.forms import ProductForm
from sales.models import Sale


# ======================
# INVENTORY LIST
# ======================
@login_required
def inventory_list(request):
    q = request.GET.get("q", "").strip()
    location_id = request.GET.get("location", "").strip()
    ordering = request.GET.get("ordering", "name").strip()

    qs = Product.objects.select_related("location").filter(is_active=True)

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(location__name__icontains=q))

    if location_id.isdigit():
        qs = qs.filter(location_id=int(location_id))

    allowed_order = {
        "name": "name",
        "-name": "-name",
        "stock": "stock",
        "-stock": "-stock",
        "sold": "sold",
        "-sold": "-sold",
    }

    qs = qs.order_by(allowed_order.get(ordering, "name"))
    total_products = qs.count()
    total_sold = qs.aggregate(x=Sum("sold"))["x"] or 0

    revenue_expr = ExpressionWrapper(
        F("quantity") * F("sell_price"),
        output_field=DecimalField(max_digits=20, decimal_places=2),
    )

    profit_expr = ExpressionWrapper(
        F("quantity") * (F("sell_price") - F("purchase_price")),
        output_field=DecimalField(max_digits=20, decimal_places=2),
    )

    totals = Sale.objects.aggregate(
        revenue=Sum(revenue_expr),
        profit=Sum(profit_expr),
    )

    locations = Location.objects.all().order_by("name")

    return render(request, "inventory/inventory_list.html", {
        "products": qs,
        "q": q,
        "locations": locations,
        "location_id": location_id,
        "ordering": ordering,
        "total_products": total_products,
        "total_sold": total_sold,
        "total_revenue": totals["revenue"] or 0,
        "total_profit": totals["profit"] or 0,
        "low_stock_count": qs.filter(stock__lte=10).count(),
    })


# ======================
# ADD / EDIT
# ======================
@login_required
def product_add(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("inventory_list")
    return render(request, "inventory/product_form.html", {"form": form, "mode": "add"})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    form = ProductForm(
        request.POST or None,
        request.FILES or None,
        instance=product
    )

    if request.method == "POST" and form.is_valid():
        product = form.save()

        # ✅ 체크박스 ON → 과거 판매 재계산
        if request.POST.get("recalc_sales"):
            Sale.objects.filter(product=product).update(
                sell_price=product.sell_price,
                purchase_price=product.purchase_price,
            )

        return redirect("inventory_list")

    return render(request, "inventory/product_form.html", {
        "form": form,
        "mode": "edit",
        "product": product,
    })

# ======================
# DELETE CONFIRM
# ======================
@require_http_methods(["GET", "POST"])
@login_required
def product_delete(request, pk):
    p = get_object_or_404(Product, pk=pk, is_active=True)

    if request.method == "POST":
        if request.POST.get("keep_sales") == "1":
            p.is_active = False
            p.save(update_fields=["is_active"])

            messages.success(request, "Product hidden, sales kept")
            return redirect("inventory_list")

    return render(request, "inventory/product_delete.html", {"p": p})

# ======================
# FORCE DELETE (WITH SALES)
# ======================
@require_http_methods(["POST"])
@login_required
def product_delete_force(request, pk):
    p = get_object_or_404(Product, pk=pk)

    Sale.objects.filter(product=p).delete()
    p.delete()

    messages.success(request, "Product and sales deleted")
    return redirect("inventory_list")
