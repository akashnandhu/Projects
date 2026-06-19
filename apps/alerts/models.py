"""
Models for managing risk alerts and counselor intervention.
"""
from django.db import models
from django.conf import settings
from apps.chat.models import ChatSession, ChatMessage

class RiskAlert(models.Model):
    """
    Alert record triggered by flagged chat messages.
    """
    ALERT_TYPES = (
        ('SELF_HARM', 'Self Harm'),
        ('PUBLIC_SAFETY', 'Public Safety'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('REVIEWED', 'Reviewed'),
        ('RESOLVED', 'Resolved'),
        ('ESCALATED', 'Escalated'),
    )

    message = models.OneToOneField(ChatMessage, on_delete=models.CASCADE, related_name='alert')
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='alerts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alerts')
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    counselor_notes = models.TextField(blank=True, null=True)
    triggered_keywords = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_alerts')

    def __str__(self):
        return f"Alert {self.id} - {self.alert_type} for {self.user.username}"
