from django.db import models
from django.utils import timezone
from djangolms.accounts.models import User
from djangolms.courses.models import Course


class Announcement(models.Model):
    """Course-specific announcements posted by instructors."""

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='announcements'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='announcements_created'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='NORMAL'
    )
    pinned = models.BooleanField(
        default=False,
        help_text='Pinned announcements appear at the top'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: Schedule announcements for future
    publish_at = models.DateTimeField(
        default=timezone.now,
        help_text='When this announcement should be visible'
    )

    class Meta:
        ordering = ['-pinned', '-created_at']
        indexes = [
            models.Index(fields=['course', '-created_at']),
            models.Index(fields=['-pinned', '-created_at']),
        ]

    def __str__(self):
        return f"{self.course.code} - {self.title}"

    def is_published(self):
        """Check if announcement is published."""
        return self.publish_at <= timezone.now()

    def get_priority_color(self):
        """Return color code for priority level."""
        colors = {
            'LOW': '#95a5a6',
            'NORMAL': '#3498db',
            'HIGH': '#f39c12',
            'URGENT': '#e74c3c',
        }
        return colors.get(self.priority, '#3498db')


class AnnouncementRead(models.Model):
    """Track which announcements have been read by which users."""

    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='read_by'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='announcements_read'
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['announcement', 'user']
        indexes = [
            models.Index(fields=['user', 'announcement']),
        ]

    def __str__(self):
        return f"{self.user.username} read {self.announcement.title}"


class Notification(models.Model):
    """User-specific notifications for various system events."""

    NOTIFICATION_TYPES = [
        ('ANNOUNCEMENT', 'New Announcement'),
        ('ASSIGNMENT', 'Assignment Posted'),
        ('SUBMISSION', 'Assignment Submitted'),
        ('GRADE', 'Assignment Graded'),
        ('ENROLLMENT', 'Course Enrollment'),
        ('SYSTEM', 'System Notification'),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    title = models.CharField(max_length=200)
    message = models.TextField()

    # Optional links to related objects
    related_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    # Optional URL for action
    action_url = models.CharField(
        max_length=500,
        blank=True,
        help_text='URL to redirect when notification is clicked'
    )

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.title} for {self.recipient.username}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def get_icon(self):
        """Return icon for notification type."""
        icons = {
            'ANNOUNCEMENT': '📢',
            'ASSIGNMENT': '📝',
            'SUBMISSION': '📤',
            'GRADE': '📊',
            'ENROLLMENT': '📚',
            'SYSTEM': '⚙️',
        }
        return icons.get(self.notification_type, '🔔')
