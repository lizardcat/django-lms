from django.contrib import admin
from .models import (
    LiveStream, StreamViewer, StreamRecording, QAQuestion,
    QuestionUpvote, StreamChat, VideoConference, VideoConferenceParticipant
)


@admin.register(LiveStream)
class LiveStreamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'instructor', 'status', 'scheduled_start', 'current_viewers', 'peak_viewers')
    list_filter = ('status', 'scheduled_start', 'enable_recording')
    search_fields = ('title', 'course__title', 'instructor__username')
    readonly_fields = ('stream_key', 'current_viewers', 'peak_viewers', 'total_views', 'created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'course', 'instructor')
        }),
        ('Schedule', {
            'fields': ('status', 'scheduled_start', 'scheduled_end', 'actual_start', 'actual_end')
        }),
        ('Streaming', {
            'fields': ('stream_key', 'enable_recording', 'recording_url')
        }),
        ('Settings', {
            'fields': ('allow_chat', 'allow_qa', 'max_viewers')
        }),
        ('Statistics', {
            'fields': ('current_viewers', 'peak_viewers', 'total_views')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(StreamViewer)
class StreamViewerAdmin(admin.ModelAdmin):
    list_display = ('user', 'stream', 'joined_at', 'left_at', 'is_currently_watching', 'total_watch_time_seconds')
    list_filter = ('is_currently_watching', 'joined_at')
    search_fields = ('user__username', 'stream__title')
    readonly_fields = ('joined_at',)


@admin.register(StreamRecording)
class StreamRecordingAdmin(admin.ModelAdmin):
    list_display = ('title', 'stream', 'duration_seconds', 'file_size_mb', 'view_count', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at', 'processed_at')
    search_fields = ('title', 'stream__title')
    readonly_fields = ('created_at', 'processed_at', 'view_count')


@admin.register(QAQuestion)
class QAQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_preview', 'user', 'stream', 'upvotes', 'is_answered', 'is_pinned', 'created_at')
    list_filter = ('is_answered', 'is_pinned', 'created_at')
    search_fields = ('question', 'user__username', 'stream__title')
    readonly_fields = ('created_at', 'answered_at')

    def question_preview(self, obj):
        return obj.question[:100] + '...' if len(obj.question) > 100 else obj.question
    question_preview.short_description = 'Question'


@admin.register(QuestionUpvote)
class QuestionUpvoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'question__question')
    readonly_fields = ('created_at',)


@admin.register(StreamChat)
class StreamChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'stream', 'message_preview', 'is_pinned', 'is_deleted', 'created_at')
    list_filter = ('is_pinned', 'is_deleted', 'created_at')
    search_fields = ('user__username', 'message', 'stream__title')
    readonly_fields = ('created_at',)

    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message'


# Video Conferencing Admin

class VideoConferenceParticipantInline(admin.TabularInline):
    """Inline admin for conference participants."""
    model = VideoConferenceParticipant
    extra = 0
    readonly_fields = ['user', 'joined_at', 'left_at', 'duration_minutes']
    fields = ['user', 'joined_at', 'left_at', 'duration_minutes', 'camera_on', 'microphone_on']
    can_delete = False


@admin.register(VideoConference)
class VideoConferenceAdmin(admin.ModelAdmin):
    """Admin interface for VideoConference model."""
    list_display = [
        'title', 'host', 'course', 'status', 'scheduled_start',
        'total_participants', 'peak_participants', 'duration_minutes'
    ]
    list_filter = ['status', 'scheduled_start', 'restrict_to_course', 'enable_recording']
    search_fields = ['title', 'description', 'host__username', 'course__code']
    readonly_fields = [
        'room_name', 'jitsi_url', 'total_participants',
        'peak_participants', 'duration_minutes', 'created_at', 'updated_at'
    ]
    ordering = ['-scheduled_start']
    inlines = [VideoConferenceParticipantInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'host', 'course')
        }),
        ('Schedule', {
            'fields': (
                'scheduled_start', 'scheduled_end',
                'actual_start', 'actual_end', 'status'
            )
        }),
        ('Jitsi Meeting', {
            'fields': ('room_name', 'jitsi_url')
        }),
        ('Security & Access', {
            'fields': (
                'require_password', 'password',
                'enable_lobby', 'restrict_to_course', 'max_participants'
            )
        }),
        ('Recording', {
            'fields': ('enable_recording', 'recording_url')
        }),
        ('Statistics', {
            'fields': (
                'total_participants', 'peak_participants', 'duration_minutes'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Auto-set host to current user if creating new conference."""
        if not change and not obj.host_id:
            obj.host = request.user
        super().save_model(request, obj, form, change)


@admin.register(VideoConferenceParticipant)
class VideoConferenceParticipantAdmin(admin.ModelAdmin):
    """Admin interface for VideoConferenceParticipant model."""
    list_display = [
        'user', 'conference', 'joined_at', 'left_at',
        'duration_minutes', 'camera_on', 'microphone_on'
    ]
    list_filter = ['joined_at', 'camera_on', 'microphone_on']
    search_fields = ['user__username', 'conference__title']
    readonly_fields = ['joined_at', 'left_at']
    ordering = ['-joined_at']

    fieldsets = (
        ('Participation Info', {
            'fields': ('conference', 'user', 'joined_at', 'left_at', 'duration_minutes')
        }),
        ('Engagement', {
            'fields': ('camera_on', 'microphone_on')
        }),
    )
