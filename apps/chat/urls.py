"""
URL patterns for the chat app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('chat/', views.chat_dashboard_view, name='chat_dashboard'),
    path('api/chat/<uuid:session_id>/history/', views.chat_history_view, name='chat_history'),
]
