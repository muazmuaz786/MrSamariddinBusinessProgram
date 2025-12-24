from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_redirect, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("lang/<str:code>/", views.set_language, name="set_language"),
]
