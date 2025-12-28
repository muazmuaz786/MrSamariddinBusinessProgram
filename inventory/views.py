from urllib import request
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F, DecimalField, ExpressionWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from inventory.models import Product, Location
from inventory.forms import ProductForm
from sales.models import Sale

from django.contrib.auth.hashers import check_password
from .models import Market

from .decorators import market_required

from django_ratelimit.decorators import ratelimit

# ======================
# INVENTORY LIST
# ======================
@market_required
def inventory_list(request):

    market_id = request.session["market_id"]

    q = request.GET.get("q", "").strip()
    location_id = request.GET.get("location", "").strip()
    ordering = request.GET.get("ordering", "name").strip()

    qs = (
        Product.objects
        .select_related("location")
        .filter(market_id=market_id, is_active=True)
    )

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

    ordering = allowed_order.get(ordering, "name")
    qs = qs.order_by(ordering)    
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

    totals = Sale.objects.filter(market_id=market_id).aggregate(
        revenue=Sum(revenue_expr),
        profit=Sum(profit_expr),
    )

    locations = Location.objects.filter(market_id=market_id).order_by("name")

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
@market_required
def product_add(request):
    market_id = request.session["market_id"]

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            request.FILES,
            market_id=market_id
        )
        if form.is_valid():
            product = form.save(commit=False)
            product.market_id = market_id
            product.save()
            return redirect("inventory_list")
    else:
        form = ProductForm(market_id=market_id)

    return render(request, "inventory/product_form.html", {
        "form": form,
        "mode": "add"
    })


@market_required
def product_edit(request, pk):
    market_id = request.session["market_id"]

    product = get_object_or_404(
        Product,
        pk=pk,
        market_id=market_id
    )

    form = ProductForm(
        request.POST or None,
        request.FILES or None,
        instance=product,
        market_id=market_id
    )

    if request.method == "POST" and form.is_valid():
        product = form.save()

        if request.POST.get("recalc_sales"):
            Sale.objects.filter(
                product=product,
                market_id=market_id
            ).update(
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
@market_required
def product_delete(request, pk):
    p = get_object_or_404(
        Product,
        pk=pk,
        market_id=request.session["market_id"],
        is_active=True
    )

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
@market_required
def product_delete_force(request, pk):
    p = get_object_or_404(
        Product,
        pk=pk,
        market_id=request.session["market_id"]
    )

    Sale.objects.filter(product=p, market_id=request.session["market_id"]).delete()
    p.delete()

    messages.success(request, "Product and sales deleted")
    return redirect("inventory_list")


from django.shortcuts import render, redirect
from .models import Market
from django.contrib import messages
from django.contrib.auth.hashers import check_password

@ratelimit(key="ip", rate="40/m", block=True)
def home(request):
    markets = Market.objects.all()

    error_market_id = None
    error_text = None

    if request.method == "POST":
        market_id = request.POST.get("market_id")
        password = request.POST.get("password")

        market = Market.objects.filter(id=market_id).first()

        if not market:
            error_market_id = market_id
            error_text = "Market not found"
        else:
            if not check_password(password, market.password_hash):
                error_market_id = market.id
                error_text = "Password is incorrect"
            else:
                request.session["market_id"] = market.id
                return redirect("inventory_list")

    return render(request, "home.html", {
        "markets": markets,
        "error_market_id": error_market_id,
        "error_text": error_text,
    })

from .models import Debt

@market_required
def debt_create(request):
    if request.method == "POST":
        customer = request.POST["customer"]
        product_id = request.POST["product_id"]
        qty = int(request.POST["quantity"])

        product = Product.objects.get(
            id=product_id,
            market_id=request.session["market_id"]
        )

        if qty <= 0 or qty > product.stock:
            messages.error(request, "Invalid quantity")
        product.stock -= qty
        product.save()

        Debt.objects.create(
            market_id=request.session["market_id"],
            product=product,
            customer_name=customer,
            quantity=qty,
        )

        return redirect("debt_list")

    products = Product.objects.filter(
        market_id=request.session["market_id"]
    )

    return render(request, "inventory/debt_create.html", {
        "products": products
    })

@market_required
def debt_pay(request, pk):
    debt = get_object_or_404(
        Debt,
        pk=pk,
        market_id=request.session["market_id"]
    )

    if request.method == "POST":
        qty = int(request.POST.get("qty"))

        if qty <= 0 or qty > debt.remaining:
            return redirect("debt_list")

        debt.returned += qty
        debt.save()

        # 💰 수익 반영
        Sale.objects.create(
            market_id=debt.market_id,
            product=debt.product,
            quantity=qty,
            sell_price=debt.product.sell_price,
            purchase_price=debt.product.purchase_price
        )

        Product.objects.filter(
            id=debt.product.id,
            market_id=debt.market_id
        ).update(
            sold=F("sold") + qty
        )

        return redirect("debt_list")



@market_required
def debt_list(request):
    market_id = request.session["market_id"]

    q = request.GET.get("q", "").strip()

    debts = Debt.objects.select_related("product").filter(market_id=market_id)

    if q:
        debts = debts.filter(
            Q(customer_name__icontains=q) |
            Q(product__name__icontains=q)
        )

    debts = debts.order_by("-created_at")

    return render(request, "inventory/debt_list.html", {
        "debts": debts,
        "q": q,
    })


@market_required
def debt_delete(request, pk):
    debt = get_object_or_404(
        Debt,
        pk=pk,
        market_id=request.session["market_id"]
    )

    if request.method == "POST":
        debt.delete()

    return redirect("debt_list")