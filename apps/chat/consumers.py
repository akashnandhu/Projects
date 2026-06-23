"""
Real-Time WebSocket Consumer for Chat.
"""
import json
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatSession, ChatMessage
from apps.alerts.models import RiskAlert
from .moderation import moderate_message
from django.utils import timezone

CRISIS_RESOURCES = {
    "SELF_HARM": {
        "hotlines": [
            {"name": "National Suicide Prevention Lifeline (US)", "number": "988"},
            {"name": "Crisis Text Line", "number": "Text HOME to 741741"},
            {"name": "International Association for Suicide Prevention", "url": "https://www.iasp.info/resources/Crisis_Centres/"},
            {"name": "iCall (India)", "number": "9152987821"},
        ],
        "breathing_exercise": "Try the 4-7-8 technique: Inhale for 4 seconds, hold for 7 seconds, exhale slowly for 8 seconds. Repeat 3 times.",
        "grounding_exercise": "Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.",
        "message": "You are not alone. What you're feeling right now is real and valid, and there are people who care and want to help."
    },
    "PUBLIC_SAFETY": {
        "hotlines": [
            {"name": "Emergency Services", "number": "911 / 112"},
            {"name": "FBI Tip Line (US)", "number": "1-800-CALL-FBI"},
            {"name": "Crisis Intervention Resources", "url": "https://www.samhsa.gov/"}
        ],
        "message": "This platform is a safe space. Expressions of violence or harm to others are taken seriously. Please reach out to appropriate services."
    }
}

EMPATHETIC_RESPONSES = [
    "I hear you. That sounds really difficult.",
    "Thank you for sharing that with me.",
    "It takes courage to talk about this.",
    "I'm here for you. We can work through this together.",
    "I'm listening. Please take your time.",
    "Your feelings are completely valid.",
    "That makes a lot of sense. Thanks for opening up.",
    "I appreciate your honesty. How can I best support you right now?"
]

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
            
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f"chat_{self.session_id}"
        
        self.session = await self.get_or_create_session(self.session_id, self.user)
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Real-time online count simulation message
        await self.send(text_data=json.dumps({
            'type': 'system_update',
            'online_staff': random.randint(3, 12)
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect."""
        if hasattr(self, 'session'):
            await self.mark_session_inactive(self.session)
            
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming WebSocket message."""
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            return
            
        message_type = text_data_json.get('type', 'chat_message')
        
        # Handle mood updates directly
        if message_type == 'mood_update':
            emotion = text_data_json.get('mood', 'neutral')
            # Echo back to confirm real-time
            await self.send(text_data=json.dumps({
                'type': 'mood_confirmation',
                'message': f"Mood logged: {emotion}"
            }))
            return

        message_content = text_data_json.get('message', '').strip()
        if not message_content:
            return

        # Moderation
        moderation_result = moderate_message(message_content)
        is_flagged = moderation_result['is_flagged']
        risk_level = moderation_result['risk_level']
        
        # Save user message
        user_message = await self.save_message(
            self.session, 'USER', message_content, is_flagged, risk_level
        )
        
        # Broadcast user message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender': 'USER',
                'id': user_message.id
            }
        )
        
        if is_flagged:
            alert_type = 'PUBLIC_SAFETY' if risk_level == 'PUBLIC_SAFETY_THREAT' else 'SELF_HARM'
            await self.create_risk_alert(user_message, self.session, self.user, alert_type, moderation_result['matched_keywords'])
            
            resources = CRISIS_RESOURCES.get(alert_type, {})
            await self.send(text_data=json.dumps({
                'type': 'crisis_intervention',
                'alert_type': alert_type,
                'resources': resources,
                'message': resources.get('message', "Please seek help.")
            }))
        else:
            # Send typing indicator immediately
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'is_typing': True
            }))
            
            # Simulate real-time bot thinking
            await asyncio.sleep(random.uniform(1.2, 2.5))
            
            bot_response_text = random.choice(EMPATHETIC_RESPONSES)
            bot_message = await self.save_message(
                self.session, 'BOT', bot_response_text, False, 'SAFE'
            )
            
            # Stop typing
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'is_typing': False
            }))
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': bot_response_text,
                    'sender': 'BOT',
                    'id': bot_message.id
                }
            )

    async def chat_message(self, event):
        """Send message to WebSocket."""
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_or_create_session(self, session_id, user):
        session, _ = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={'user': user, 'is_active': True}
        )
        return session

    @database_sync_to_async
    def mark_session_inactive(self, session):
        session.is_active = False
        session.ended_at = timezone.now()
        session.save()

    @database_sync_to_async
    def save_message(self, session, sender_type, content, is_flagged, risk_level):
        return ChatMessage.objects.create(
            session=session,
            sender_type=sender_type,
            content=content,
            is_flagged=is_flagged,
            risk_level=risk_level
        )

    @database_sync_to_async
    def create_risk_alert(self, message, session, user, alert_type, keywords):
        RiskAlert.objects.create(
            message=message,
            session=session,
            user=user,
            alert_type=alert_type,
            triggered_keywords=keywords
        )
