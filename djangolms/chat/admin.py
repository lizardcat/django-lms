from django.contrib import admin
from .models import ChatRoom, Message, MessageReadReceipt, UserPresence, ChatNotification


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'course', 'is_active', 'created_by', 'created_at')
    list_filter = ('room_type', 'is_active', 'created_at')
    search_fields = ('name', 'course__title')
    filter_horizontal = ('participants',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Room Details', {
            'fields': ('name', 'room_type', 'course')
        }),
        ('Participants', {
            'fields': ('participants',)
        }),
        ('Settings', {
            'fields': ('is_active', 'allow_file_sharing')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'room', 'message_type', 'content_preview', 'created_at', 'is_edited', 'is_deleted')
    list_filter = ('message_type', 'is_edited', 'is_deleted', 'created_at')
    search_fields = ('content', 'sender__username', 'room__name')
    readonly_fields = ('created_at', 'updated_at')

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(MessageReadReceipt)
class MessageReadReceiptAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('user__username', 'message__content')
    readonly_fields = ('read_at',)


@admin.register(UserPresence)
class UserPresenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'is_online', 'is_typing', 'last_seen')
    list_filter = ('is_online', 'is_typing', 'last_seen')
    search_fields = ('user__username', 'room__name')
    readonly_fields = ('last_seen',)


@admin.register(ChatNotification)
class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'room__name')
    readonly_fields = ('created_at',)
