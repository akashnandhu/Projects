"""
Forms for user registration and authentication.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    """
    Registration form with email, username, password, and anonymity mode toggle.
    """
    class Meta(UserCreationForm.Meta):
        model = UserProfile
        fields = UserCreationForm.Meta.fields + ('email', 'is_anonymous_mode')
        help_texts = {
            'is_anonymous_mode': "Enable this to replace your display name with an alias in chats."
        }
