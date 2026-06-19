"""
Management command to close chat sessions inactive for more than 24 hours.
Ready for cron/Celery integration.
"""
from django.core.management.base import BaseCommand
from apps.chat.models import ChatSession
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Closes chat sessions that have been inactive for over 24 hours'

    def handle(self, *args, **options):
        threshold = timezone.now() - timedelta(hours=24)
        
        stale_sessions = ChatSession.objects.filter(is_active=True).exclude(
            messages__timestamp__gte=threshold
        ).filter(started_at__lt=threshold)
        
        count = stale_sessions.count()
        
        for session in stale_sessions:
            session.is_active = False
            session.ended_at = timezone.now()
            session.save()
            
        self.stdout.write(self.style.SUCCESS(f'Successfully closed {count} stale chat sessions.'))
