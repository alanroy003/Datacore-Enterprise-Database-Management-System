# file: config/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/',   SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/',  SpectacularRedocView.as_view(url_name='schema'),   name='redoc'),
    path('api/auth/',   include('apps.accounts.urls')),
    path('api/',        include('apps.companies.urls')),
    path('api/',        include('apps.assets.urls')),
    path('api/',        include('apps.operations.urls')),
    path('api/',        include('apps.notifications.urls')),
    path('api/',        include('apps.core.urls')),
]