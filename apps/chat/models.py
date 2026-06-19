"""
Models for chat sessions and messages.
"""
from django.db import models
from django.conf import settings
import uuid

class ChatSession(models.Model):
    """
    Represents a real-time chat session.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.session_id} for {self.user.username}"

class ChatMessage(models.Model):
    """
    Represents a single message in a chat session.
    # TODO: In production, use django-encrypted-model-fields for `content` to secure PII.
    """
    SENDER_CHOICES = (
        ('USER', 'User'),
        ('BOT', 'Bot'),
        ('SYSTEM', 'System'),
    )

    RISK_CHOICES = (
        ('SAFE', 'Safe'),
        ('SELF_HARM_RISK', 'Self Harm Risk'),
        ('PUBLIC_SAFETY_THREAT', 'Public Safety Threat'),
    )

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    is_flagged = models.BooleanField(default=False)
    risk_level = models.CharField(max_length=30, choices=RISK_CHOICES, default='SAFE')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender_type}: {self.content[:30]}"
