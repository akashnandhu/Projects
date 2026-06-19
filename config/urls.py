"""
Master URL config including all app urls and WebSocket routing.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    """Health Check Endpoint."""
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', include('apps.chat.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('alerts/', include('apps.alerts.urls')),
]
