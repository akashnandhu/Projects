"""
URL patterns for the alerts app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.AlertDashboardView.as_view(), name='alert_dashboard'),
    path('<int:pk>/', views.AlertDetailView.as_view(), name='alert_detail'),
    path('<int:pk>/resolve/', views.alert_resolve_view, name='alert_resolve'),
]
