from django.shortcuts import redirect
from functools import wraps

def market_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("market_id"):
            return redirect("home")
        return view(request, *args, **kwargs)
    return wrapper