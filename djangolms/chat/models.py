from django.db import models
from django.conf import settings
from djangolms.courses.models import Course


class ChatRoom(models.Model):
    """Chat rooms for courses or direct messages"""
    ROOM_TYPES = [
        ('COURSE', 'Course Chat'),
        ('DIRECT', 'Direct Message'),
        ('GROUP', 'Group Chat'),
    ]

    name = models.CharField(max_length=200)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='COURSE')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_rooms')

    # For group chats and DMs
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms', blank=True)

    # Settings
    is_active = models.BooleanField(default=True)
    allow_file_sharing = models.BooleanField(default=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

    @property
    def online_users(self):
        """Get currently online users in this room"""
        return UserPresence.objects.filter(room=self, is_online=True).select_related('user')


class Message(models.Model):
    """Chat messages"""
    MESSAGE_TYPES = [
        ('TEXT', 'Text Message'),
        ('FILE', 'File Attachment'),
        ('IMAGE', 'Image'),
        ('SYSTEM', 'System Message'),
    ]

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')

    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='TEXT')
    content = models.TextField()

    # File attachments
    file = models.FileField(upload_to='chat/files/%Y/%m/', null=True, blank=True)

    # Reply functionality
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

    # Message status
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', '-created_at']),
            models.Index(fields=['sender', '-created_at']),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

    @property
    def read_by_count(self):
        """Count how many users have read this message"""
        return self.read_receipts.count()


class MessageReadReceipt(models.Model):
    """Track who has read which messages"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_receipts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['message', 'user']
        indexes = [
            models.Index(fields=['user', '-read_at']),
        ]

    def __str__(self):
        return f"{self.user.username} read message {self.message.id}"


class UserPresence(models.Model):
    """Track user presence in chat rooms"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='presence')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='user_presence')

    is_online = models.BooleanField(default=False)
    is_typing = models.BooleanField(default=False)

    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'room']
        indexes = [
            models.Index(fields=['room', 'is_online']),
        ]

    def __str__(self):
        status = "Online" if self.is_online else "Offline"
        return f"{self.user.username} in {self.room.name} - {status}"


class ChatNotification(models.Model):
    """Notifications for unread messages"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_notifications')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]

    def __str__(self):
        return f"Notification for {self.user.username} in {self.room.name}"
