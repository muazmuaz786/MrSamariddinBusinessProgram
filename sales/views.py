from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from inventory.models import Product
from .models import Sale

@login_required
def sell_page(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "sales/sell_form.html", {
        "product": product
    })


@require_POST
@login_required
def sell_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    try:
        quantity = int(request.POST.get("quantity"))
    except:
        messages.error(request, "Invalid quantity")
        return redirect("sell_page", pk=pk)

    if quantity <= 0:
        messages.error(request, "Quantity must be positive")
        return redirect("sell_page", pk=pk)

    if quantity > product.stock:
        messages.error(
            request,
            f"Not enough stock. Available: {product.stock}"
        )
        return redirect("sell_page", pk=pk)

    product.stock -= quantity
    product.sold += quantity
    product.save(update_fields=["stock", "sold"])

 
    Sale.objects.create(
        product=product,
        quantity=quantity,
        sell_price=product.sell_price,
        purchase_price=product.purchase_price,
    )

    messages.success(request, f"Sold {quantity} item(s)")
    return redirect("inventory_list")
