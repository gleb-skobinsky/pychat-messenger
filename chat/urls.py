from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import signup, signin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("login/", signin, name="login"),
    path("logout/", signin, name="logout"),
    path("signup/", signup, name="signup"),
]
