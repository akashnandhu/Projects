"""
Views for the alerts dashboard and details.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.db import models
from django.db.models import Count
from django.views.generic import ListView, DetailView
from .models import RiskAlert
from django.utils import timezone
from django.contrib import contenttypes

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class AlertDashboardView(StaffRequiredMixin, ListView):
    """
    Dashboard for all RiskAlert records.
    """
    model = RiskAlert
    template_name = 'chat/dashboard.html'
    context_object_name = 'alerts'
    paginate_by = 20

    def get_queryset(self):
        queryset = RiskAlert.objects.select_related('user', 'message').order_by('-created_at')
        status = self.request.GET.get('status')
        alert_type = self.request.GET.get('type')
        if status:
            queryset = queryset.filter(status=status)
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = RiskAlert.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=models.Q(status='PENDING')),
            resolved=Count('id', filter=models.Q(status='RESOLVED')),
            escalated=Count('id', filter=models.Q(status='ESCALATED')),
        )
        context['stats'] = stats
        return context

class AlertDetailView(StaffRequiredMixin, DetailView):
    """
    Shows detail of a specific alert.
    """
    model = RiskAlert
    template_name = 'alerts/alert_detail.html'
    context_object_name = 'alert'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        alert = self.get_object()
        session = alert.session
        messages = session.messages.all().order_by('timestamp')
        context['chat_messages'] = messages
        return context

    def post(self, request, *args, **kwargs):
        alert = self.get_object()
        new_status = request.POST.get('status')
        notes = request.POST.get('counselor_notes')
        
        if new_status in dict(RiskAlert.STATUS_CHOICES):
            alert.status = new_status
            if new_status == 'RESOLVED' and not alert.resolved_at:
                alert.resolved_at = timezone.now()
                
        if notes:
            alert.counselor_notes = notes
            
        alert.reviewed_by = request.user
        alert.save()
        
        return redirect('alert_detail', pk=alert.pk)

@user_passes_test(lambda u: u.is_staff)
def alert_resolve_view(request, pk):
    """AJAX compatible POST endpoint to update alert status."""
    if request.method == 'POST':
        alert = get_object_or_404(RiskAlert, pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(RiskAlert.STATUS_CHOICES):
            alert.status = new_status
            if new_status == 'RESOLVED' and not alert.resolved_at:
                alert.resolved_at = timezone.now()
            alert.reviewed_by = request.user
            alert.save()
            return JsonResponse({'status': 'success', 'new_status': alert.status})
        return JsonResponse({'status': 'invalid status'}, status=400)
    return JsonResponse({'status': 'bad request'}, status=400)
