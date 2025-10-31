from django.contrib import admin
from django.utils.html import format_html
from .models import Announcement, AnnouncementRead, Notification


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """Admin interface for Announcement model."""

    list_display = [
        'title',
        'course',
        'author',
        'priority_badge',
        'pinned',
        'is_published_status',
        'created_at',
    ]
    list_filter = ['priority', 'pinned', 'created_at', 'course']
    search_fields = ['title', 'content', 'course__title', 'course__code']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'author', 'title', 'content')
        }),
        ('Settings', {
            'fields': ('priority', 'pinned', 'publish_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def priority_badge(self, obj):
        """Display priority with color badge."""
        color = obj.get_priority_color()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'

    def is_published_status(self, obj):
        """Show if announcement is published."""
        if obj.is_published():
            return format_html(
                '<span style="color: green;">✓ Published</span>'
            )
        return format_html(
            '<span style="color: orange;">⏱ Scheduled</span>'
        )
    is_published_status.short_description = 'Status'


@admin.register(AnnouncementRead)
class AnnouncementReadAdmin(admin.ModelAdmin):
    """Admin interface for AnnouncementRead model."""

    list_display = ['user', 'announcement', 'read_at']
    list_filter = ['read_at', 'announcement__course']
    search_fields = ['user__username', 'user__email', 'announcement__title']
    date_hierarchy = 'read_at'
    readonly_fields = ['read_at']

    def has_add_permission(self, request):
        """Prevent manual creation of read records."""
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""

    list_display = [
        'icon_display',
        'title',
        'recipient',
        'notification_type',
        'is_read_status',
        'created_at',
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username', 'recipient__email']
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Recipient', {
            'fields': ('recipient',)
        }),
        ('Content', {
            'fields': ('notification_type', 'title', 'message')
        }),
        ('Related Objects', {
            'fields': ('related_course', 'related_announcement', 'action_url'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'created_at')
        }),
    )

    actions = ['mark_as_read', 'mark_as_unread']

    def icon_display(self, obj):
        """Display icon for notification type."""
        return obj.get_icon()
    icon_display.short_description = ''

    def is_read_status(self, obj):
        """Show read/unread status with color."""
        if obj.is_read:
            return format_html(
                '<span style="color: green;">✓ Read</span>'
            )
        return format_html(
            '<span style="color: #e74c3c; font-weight: bold;">● Unread</span>'
        )
    is_read_status.short_description = 'Status'

    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        count = queryset.filter(is_read=False).update(is_read=True)
        self.message_user(request, f'{count} notification(s) marked as read.')
    mark_as_read.short_description = 'Mark selected as read'

    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread."""
        count = queryset.filter(is_read=True).update(is_read=False, read_at=None)
        self.message_user(request, f'{count} notification(s) marked as unread.')
    mark_as_unread.short_description = 'Mark selected as unread'
