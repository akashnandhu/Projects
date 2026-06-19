"""
Models for user authentication and profiles.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserProfile(AbstractUser):
    """
    Custom user model extending AbstractUser.
    Includes an anonymous mode and preferred language.
    """
    is_anonymous_mode = models.BooleanField(
        default=False,
        help_text="When enabled, display name is replaced with a randomly generated alias in chat logs."
    )
    preferred_language = models.CharField(
        max_length=10, 
        default='en',
        help_text="For future localization of crisis resources"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_display_alias(self):
        """Returns the appropriate display name depending on anonymity mode."""
        if self.is_anonymous_mode:
            id_val = self.id if self.id else 0
            return f"Anonymous Sparrow #{4821 + id_val}"
        return self.username
