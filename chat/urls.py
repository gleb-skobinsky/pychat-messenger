from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import signup, signin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("login/", signin, name="login"),
    path("logout/", signin, name="logout"),
    path("signup/", signup, name="signup"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
