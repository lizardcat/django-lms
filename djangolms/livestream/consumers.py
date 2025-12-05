"""
WebSocket consumers for livestreaming functionality
Handles WebRTC signaling and stream chat
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class LiveStreamConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for livestream viewers"""

    async def connect(self):
        self.stream_id = self.scope['url_route']['kwargs']['stream_id']
        self.stream_group_name = f'livestream_{self.stream_id}'
        self.user = self.scope['user']

        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return

        # Verify user has access to this stream
        has_access = await self.check_stream_access()
        if not has_access:
            await self.close()
            return

        # Join stream group
        await self.channel_layer.group_add(
            self.stream_group_name,
            self.channel_name
        )

        await self.accept()

        # Add viewer
        await self.add_viewer()

        # Send current viewer count to all
        viewer_count = await self.get_viewer_count()
        await self.channel_layer.group_send(
            self.stream_group_name,
            {
                'type': 'viewer_count',
                'count': viewer_count,
            }
        )

    async def disconnect(self, close_code):
        # Remove viewer
        await self.remove_viewer()

        # Send updated viewer count
        viewer_count = await self.get_viewer_count()
        await self.channel_layer.group_send(
            self.stream_group_name,
            {
                'type': 'viewer_count',
                'count': viewer_count,
            }
        )

        # Leave stream group
        await self.channel_layer.group_discard(
            self.stream_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Receive message from WebSocket"""
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'chat':
            await self.handle_chat(data)
        elif message_type == 'qa_question':
            await self.handle_qa_question(data)
        elif message_type == 'upvote':
            await self.handle_upvote(data)
        elif message_type == 'webrtc_offer':
            await self.handle_webrtc_offer(data)
        elif message_type == 'webrtc_answer':
            await self.handle_webrtc_answer(data)
        elif message_type == 'webrtc_ice':
            await self.handle_webrtc_ice(data)

    async def handle_chat(self, data):
        """Handle chat message during stream"""
        message = data.get('message', '').strip()

        if not message:
            return

        # Save chat message
        chat_msg = await self.save_chat_message(message)

        # Broadcast to all viewers
        await self.channel_layer.group_send(
            self.stream_group_name,
            {
                'type': 'stream_chat',
                'message': await self.serialize_chat_message(chat_msg),
            }
        )

    async def handle_qa_question(self, data):
        """Handle Q&A question"""
        question_text = data.get('question', '').strip()

        if not question_text:
            return

        # Save question
        question = await self.save_qa_question(question_text)

        # Broadcast to all viewers
        await self.channel_layer.group_send(
            self.stream_group_name,
            {
                'type': 'qa_question_event',
                'question': await self.serialize_qa_question(question),
            }
        )

    async def handle_upvote(self, data):
        """Handle upvote on Q&A question"""
        question_id = data.get('question_id')

        if not question_id:
            return

        result = await self.toggle_upvote(question_id)

        if result:
            # Broadcast updated question
            await self.channel_layer.group_send(
                self.stream_group_name,
                {
                    'type': 'qa_upvote',
                    'question_id': question_id,
                    'upvotes': result['upvotes'],
                }
            )

    async def handle_webrtc_offer(self, data):
        """Handle WebRTC offer (for peer-to-peer streaming)"""
        await self.channel_layer.group_send(
            self.stream_group_name,
            {
                'type': 'webrtc_offer_event',
                'offer': data.get('offer'),
                'sender_id': self.user.id,
            }
        )

    async def handle_webrtc_answer(self, data):
        """Handle WebRTC answer"""
        await self.channel_layer.group_send(
            self.stream_group_name,
            {
                'type': 'webrtc_answer_event',
                'answer': data.get('answer'),
                'sender_id': self.user.id,
            }
        )

    async def handle_webrtc_ice(self, data):
        """Handle WebRTC ICE candidate"""
        await self.channel_layer.group_send(
            self.stream_group_name,
            {
                'type': 'webrtc_ice_event',
                'candidate': data.get('candidate'),
                'sender_id': self.user.id,
            }
        )

    # Event handlers (messages from group)

    async def viewer_count(self, event):
        """Send viewer count update"""
        await self.send(text_data=json.dumps({
            'type': 'viewer_count',
            'count': event['count'],
        }))

    async def stream_chat(self, event):
        """Send chat message"""
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
        }))

    async def qa_question_event(self, event):
        """Send Q&A question"""
        await self.send(text_data=json.dumps({
            'type': 'qa_question',
            'question': event['question'],
        }))

    async def qa_upvote(self, event):
        """Send Q&A upvote update"""
        await self.send(text_data=json.dumps({
            'type': 'qa_upvote',
            'question_id': event['question_id'],
            'upvotes': event['upvotes'],
        }))

    async def webrtc_offer_event(self, event):
        """Forward WebRTC offer"""
        if event['sender_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_offer',
                'offer': event['offer'],
                'sender_id': event['sender_id'],
            }))

    async def webrtc_answer_event(self, event):
        """Forward WebRTC answer"""
        if event['sender_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_answer',
                'answer': event['answer'],
                'sender_id': event['sender_id'],
            }))

    async def webrtc_ice_event(self, event):
        """Forward WebRTC ICE candidate"""
        if event['sender_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_ice',
                'candidate': event['candidate'],
                'sender_id': event['sender_id'],
            }))

    async def stream_status(self, event):
        """Send stream status update"""
        await self.send(text_data=json.dumps({
            'type': 'stream_status',
            'status': event['status'],
        }))

    # Database operations

    @database_sync_to_async
    def add_viewer(self):
        """Add viewer to stream"""
        from .models import LiveStream, StreamViewer

        stream = LiveStream.objects.get(id=self.stream_id)

        viewer, created = StreamViewer.objects.get_or_create(
            stream=stream,
            user=self.user,
            is_currently_watching=True,
            defaults={'joined_at': timezone.now()}
        )

        if not created and not viewer.is_currently_watching:
            viewer.is_currently_watching = True
            viewer.joined_at = timezone.now()
            viewer.save()

        # Update stream stats
        stream.current_viewers = StreamViewer.objects.filter(
            stream=stream,
            is_currently_watching=True
        ).count()

        if stream.current_viewers > stream.peak_viewers:
            stream.peak_viewers = stream.current_viewers

        stream.total_views += 1
        stream.save()

    @database_sync_to_async
    def remove_viewer(self):
        """Remove viewer from stream"""
        from .models import LiveStream, StreamViewer

        stream = LiveStream.objects.get(id=self.stream_id)

        try:
            viewer = StreamViewer.objects.get(
                stream=stream,
                user=self.user,
                is_currently_watching=True
            )
            viewer.is_currently_watching = False
            viewer.left_at = timezone.now()

            # Calculate watch time
            if viewer.joined_at:
                watch_time = (timezone.now() - viewer.joined_at).total_seconds()
                viewer.total_watch_time_seconds += int(watch_time)

            viewer.save()

        except StreamViewer.DoesNotExist:
            pass

        # Update stream stats
        stream.current_viewers = StreamViewer.objects.filter(
            stream=stream,
            is_currently_watching=True
        ).count()
        stream.save()

    @database_sync_to_async
    def get_viewer_count(self):
        """Get current viewer count"""
        from .models import StreamViewer
        return StreamViewer.objects.filter(
            stream_id=self.stream_id,
            is_currently_watching=True
        ).count()

    @database_sync_to_async
    def save_chat_message(self, message):
        """Save chat message"""
        from .models import LiveStream, StreamChat

        stream = LiveStream.objects.get(id=self.stream_id)

        chat_msg = StreamChat.objects.create(
            stream=stream,
            user=self.user,
            message=message
        )

        return chat_msg

    @database_sync_to_async
    def serialize_chat_message(self, chat_msg):
        """Serialize chat message"""
        return {
            'id': chat_msg.id,
            'user_id': chat_msg.user.id,
            'username': chat_msg.user.username,
            'user_full_name': chat_msg.user.get_full_name() or chat_msg.user.username,
            'message': chat_msg.message,
            'created_at': chat_msg.created_at.isoformat(),
            'is_pinned': chat_msg.is_pinned,
        }

    @database_sync_to_async
    def save_qa_question(self, question_text):
        """Save Q&A question"""
        from .models import LiveStream, QAQuestion

        stream = LiveStream.objects.get(id=self.stream_id)

        question = QAQuestion.objects.create(
            stream=stream,
            user=self.user,
            question=question_text
        )

        return question

    @database_sync_to_async
    def serialize_qa_question(self, question):
        """Serialize Q&A question"""
        return {
            'id': question.id,
            'user_id': question.user.id,
            'username': question.user.username,
            'question': question.question,
            'upvotes': question.upvotes,
            'is_answered': question.is_answered,
            'answer': question.answer,
            'is_pinned': question.is_pinned,
            'created_at': question.created_at.isoformat(),
        }

    @database_sync_to_async
    def toggle_upvote(self, question_id):
        """Toggle upvote on question"""
        from .models import QAQuestion, QuestionUpvote

        try:
            question = QAQuestion.objects.get(id=question_id, stream_id=self.stream_id)

            upvote, created = QuestionUpvote.objects.get_or_create(
                question=question,
                user=self.user
            )

            if not created:
                # Remove upvote
                upvote.delete()
                question.upvotes = max(0, question.upvotes - 1)
            else:
                # Add upvote
                question.upvotes += 1

            question.save()

            return {'upvotes': question.upvotes}

        except QAQuestion.DoesNotExist:
            return None

    @database_sync_to_async
    def check_stream_access(self):
        """Check if user has access to this stream"""
        from .models import LiveStream
        from djangolms.courses.models import Enrollment

        try:
            stream = LiveStream.objects.get(id=self.stream_id)

            # Instructors can always access their own streams
            if stream.instructor == self.user:
                return True

            # Check if user is enrolled in the course
            if Enrollment.objects.filter(
                student=self.user,
                course=stream.course,
                status='ENROLLED'
            ).exists():
                return True

            return False

        except LiveStream.DoesNotExist:
            return False
