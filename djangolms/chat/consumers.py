"""
WebSocket consumers for real-time chat functionality
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for chat rooms"""

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Update user presence
        await self.set_user_online(True)

        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'user_id': self.user.id,
                'username': self.user.username,
            }
        )

    async def disconnect(self, close_code):
        # Update user presence
        await self.set_user_online(False)

        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_leave',
                'user_id': self.user.id,
                'username': self.user.username,
            }
        )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Receive message from WebSocket"""
        data = json.loads(text_data)
        message_type = data.get('type', 'message')

        if message_type == 'message':
            await self.handle_message(data)
        elif message_type == 'typing':
            await self.handle_typing(data)
        elif message_type == 'read':
            await self.handle_read_receipt(data)

    async def handle_message(self, data):
        """Handle chat message"""
        content = data.get('content', '')
        reply_to_id = data.get('reply_to', None)

        if not content.strip():
            return

        # Save message to database
        message = await self.save_message(content, reply_to_id)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': await self.serialize_message(message),
            }
        )

    async def handle_typing(self, data):
        """Handle typing indicator"""
        is_typing = data.get('is_typing', False)

        await self.set_user_typing(is_typing)

        # Broadcast typing status
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': is_typing,
            }
        )

    async def handle_read_receipt(self, data):
        """Handle message read receipt"""
        message_id = data.get('message_id')

        if message_id:
            await self.mark_message_read(message_id)

    # Handlers for different event types

    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
        }))

    async def user_join(self, event):
        """Send user join notification"""
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'user_id': event['user_id'],
            'username': event['username'],
        }))

    async def user_leave(self, event):
        """Send user leave notification"""
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'user_id': event['user_id'],
            'username': event['username'],
        }))

    async def typing_indicator(self, event):
        """Send typing indicator"""
        # Don't send typing indicator to the user who is typing
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing'],
            }))

    # Database operations

    @database_sync_to_async
    def save_message(self, content, reply_to_id=None):
        """Save message to database"""
        from .models import Message, ChatRoom

        room = ChatRoom.objects.get(id=self.room_id)
        reply_to = None

        if reply_to_id:
            try:
                reply_to = Message.objects.get(id=reply_to_id, room=room)
            except Message.DoesNotExist:
                pass

        message = Message.objects.create(
            room=room,
            sender=self.user,
            content=content,
            message_type='TEXT',
            reply_to=reply_to
        )

        # Create notifications for other participants
        self.create_notifications(message)

        return message

    @database_sync_to_async
    def serialize_message(self, message):
        """Serialize message for JSON"""
        return {
            'id': message.id,
            'sender_id': message.sender.id,
            'sender_name': message.sender.get_full_name() or message.sender.username,
            'sender_username': message.sender.username,
            'content': message.content,
            'message_type': message.message_type,
            'reply_to': message.reply_to.id if message.reply_to else None,
            'created_at': message.created_at.isoformat(),
            'is_edited': message.is_edited,
        }

    @database_sync_to_async
    def set_user_online(self, is_online):
        """Update user online status"""
        from .models import UserPresence, ChatRoom

        room = ChatRoom.objects.get(id=self.room_id)
        presence, created = UserPresence.objects.get_or_create(
            user=self.user,
            room=room,
            defaults={'is_online': is_online}
        )

        if not created:
            presence.is_online = is_online
            presence.save()

    @database_sync_to_async
    def set_user_typing(self, is_typing):
        """Update user typing status"""
        from .models import UserPresence, ChatRoom

        room = ChatRoom.objects.get(id=self.room_id)
        presence, created = UserPresence.objects.get_or_create(
            user=self.user,
            room=room,
            defaults={'is_typing': is_typing}
        )

        if not created:
            presence.is_typing = is_typing
            presence.save()

    @database_sync_to_async
    def mark_message_read(self, message_id):
        """Mark message as read"""
        from .models import Message, MessageReadReceipt

        try:
            message = Message.objects.get(id=message_id, room_id=self.room_id)
            MessageReadReceipt.objects.get_or_create(
                message=message,
                user=self.user
            )
        except Message.DoesNotExist:
            pass

    @database_sync_to_async
    def create_notifications(self, message):
        """Create notifications for room participants"""
        from .models import ChatNotification, ChatRoom

        room = ChatRoom.objects.get(id=self.room_id)

        # Get all participants except the sender
        if room.room_type == 'COURSE':
            # For course rooms, notify all enrolled students and instructors
            from djangolms.courses.models import Enrollment
            enrollments = Enrollment.objects.filter(course=room.course, status='ENROLLED')
            users = [e.student for e in enrollments if e.student != self.user]

            # Add instructor if not the sender
            if room.course.instructor != self.user:
                users.append(room.course.instructor)
        else:
            # For group/DM, notify all participants except sender
            users = room.participants.exclude(id=self.user.id)

        # Create notifications
        for user in users:
            ChatNotification.objects.create(
                user=user,
                room=room,
                message=message
            )
