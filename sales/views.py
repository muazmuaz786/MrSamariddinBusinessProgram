from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from sales.forms import SellForm
from inventory.models import Product
from .models import Sale
from inventory.decorators import market_required
from django.db import transaction
from .forms import SellForm

@market_required
def sell_page(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        market_id=request.session["market_id"]
    )
    return render(request, "sales/sell_form.html", {
        "product": product
    })

@require_POST
@market_required
def sell_product(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        market_id=request.session["market_id"]
    )

    form = SellForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Invalid quantity")
        return redirect("sell_page", pk=pk)

    quantity = form.cleaned_data["quantity"]

    if quantity > product.stock:
        messages.error(
            request,
            f"Not enough stock. Available: {product.stock}"
        )
        return redirect("sell_page", pk=pk)

    with transaction.atomic():
        product.stock -= quantity
        product.sold += quantity
        product.save(update_fields=["stock", "sold"])

        Sale.objects.create(
            market_id=request.session["market_id"],
            product=product,
            quantity=quantity,
            sell_price=product.sell_price,
            purchase_price=product.purchase_price,
        )

    messages.success(request, f"Sold {quantity} item(s)")
    return redirect("inventory_list")