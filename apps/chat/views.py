"""
Views for handling chat interface and operations.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatSession, ChatMessage
from django.core.paginator import Paginator

def home_view(request):
    """Public landing page."""
    if request.user.is_authenticated:
        return redirect('chat_dashboard')
    return redirect('login')

@login_required
def chat_dashboard_view(request):
    """Renders the chat UI."""
    session = ChatSession.objects.filter(user=request.user, is_active=True).first()
    if not session:
        session = ChatSession.objects.create(user=request.user)
        
    return render(request, 'chat/chat.html', {
        'session_id': session.session_id,
        'user_alias': request.user.get_display_alias() if hasattr(request.user, 'get_display_alias') else request.user.username
    })

@login_required
def chat_history_view(request, session_id):
    """Returns paginated past messages for a session as JSON."""
    try:
        session = ChatSession.objects.get(session_id=session_id, user=request.user)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
        
    messages_query = session.messages.all().order_by('-timestamp')
    paginator = Paginator(messages_query, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    data = []
    for msg in page_obj:
        data.append({
            'sender': msg.sender_type,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat()
        })
    data.reverse()
    
    return JsonResponse({
        'messages': data,
        'has_next': page_obj.has_next()
    })
