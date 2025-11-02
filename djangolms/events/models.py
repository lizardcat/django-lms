from django.db import models
from django.conf import settings
from django.utils import timezone
from djangolms.courses.models import Course


class Event(models.Model):
    """
    Calendar event model for tracking academic events, deadlines, and reminders.
    """
    class EventType(models.TextChoices):
        ASSIGNMENT = 'ASSIGNMENT', 'Assignment Due'
        EXAM = 'EXAM', 'Exam'
        QUIZ = 'QUIZ', 'Quiz'
        CLASS = 'CLASS', 'Class Session'
        OFFICE_HOURS = 'OFFICE_HOURS', 'Office Hours'
        REMINDER = 'REMINDER', 'Reminder'
        OTHER = 'OTHER', 'Other'

    title = models.CharField(max_length=200, help_text="Event title")
    description = models.TextField(blank=True, help_text="Event description")
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.OTHER,
        help_text="Type of event"
    )

    # Date/Time fields
    start_date = models.DateTimeField(help_text="Event start date and time")
    end_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Event end date and time (optional)"
    )
    all_day = models.BooleanField(
        default=False,
        help_text="Is this an all-day event?"
    )

    # Relations
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='events',
        blank=True,
        null=True,
        help_text="Associated course (optional)"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_events',
        help_text="User who created this event"
    )

    # Visual customization
    color = models.CharField(
        max_length=7,
        default='#007bff',
        help_text="Hex color code for event display"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['start_date']

    def __str__(self):
        if self.course:
            return f"{self.course.code} - {self.title}"
        return self.title

    @property
    def is_past(self):
        """Check if event is in the past."""
        event_date = self.end_date if self.end_date else self.start_date
        return timezone.now() > event_date

    @property
    def is_today(self):
        """Check if event is today."""
        now = timezone.now()
        return self.start_date.date() == now.date()

    @property
    def duration(self):
        """Calculate event duration in minutes."""
        if self.end_date:
            return (self.end_date - self.start_date).total_seconds() / 60
        return None
