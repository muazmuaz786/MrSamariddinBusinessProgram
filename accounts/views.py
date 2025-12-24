from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import translation
from django.http import HttpResponseBadRequest

def login_view(request):
    if request.user.is_authenticated:
        return redirect("inventory_list")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("inventory_list")
        return render(request, "accounts/login.html", {"error": "Invalid username or password"})
    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def home_redirect(request):
    return redirect("inventory_list")

def set_language(request, code: str):
    if code not in ("uz", "ru"):
        return HttpResponseBadRequest("Invalid language")

    translation.activate(code)
    request.session[settings.LANGUAGE_COOKIE_NAME] = code  
    next_url = request.GET.get("next") or "inventory_list"
    return redirect(next_url)
