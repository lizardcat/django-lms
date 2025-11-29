from django.db import models
from django.conf import settings
from djangolms.courses.models import Course


class LiveStream(models.Model):
    """Live streaming sessions"""
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live'),
        ('ENDED', 'Ended'),
        ('CANCELLED', 'Cancelled'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='livestreams')
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hosted_streams')

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Streaming details
    stream_key = models.CharField(max_length=100, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')

    # Schedule
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)

    # Recording
    enable_recording = models.BooleanField(default=True)
    recording_url = models.URLField(blank=True)

    # Settings
    allow_chat = models.BooleanField(default=True)
    allow_qa = models.BooleanField(default=True)
    max_viewers = models.IntegerField(default=1000, help_text="Maximum concurrent viewers")

    # Stats
    current_viewers = models.IntegerField(default=0)
    peak_viewers = models.IntegerField(default=0)
    total_views = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_start']
        indexes = [
            models.Index(fields=['course', 'status']),
            models.Index(fields=['instructor', '-scheduled_start']),
        ]

    def __str__(self):
        return f"{self.title} - {self.course.title}"

    def save(self, *args, **kwargs):
        if not self.stream_key:
            import uuid
            self.stream_key = str(uuid.uuid4())
        super().save(*args, **kwargs)

    @property
    def is_live(self):
        return self.status == 'LIVE'

    @property
    def duration_minutes(self):
        """Calculate stream duration in minutes"""
        if self.actual_start and self.actual_end:
            delta = self.actual_end - self.actual_start
            return int(delta.total_seconds() / 60)
        return 0


class StreamViewer(models.Model):
    """Track viewers of a livestream"""
    stream = models.ForeignKey(LiveStream, on_delete=models.CASCADE, related_name='viewers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watched_streams')

    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    is_currently_watching = models.BooleanField(default=True)

    # Engagement
    total_watch_time_seconds = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['stream', 'is_currently_watching']),
        ]

    def __str__(self):
        return f"{self.user.username} watching {self.stream.title}"


class StreamRecording(models.Model):
    """Recorded livestream sessions"""
    stream = models.OneToOneField(LiveStream, on_delete=models.CASCADE, related_name='recording')

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    video_file = models.FileField(upload_to='stream_recordings/%Y/%m/', null=True, blank=True)
    video_url = models.URLField(blank=True, help_text="External URL if hosted elsewhere")

    thumbnail = models.ImageField(upload_to='stream_thumbnails/', null=True, blank=True)

    duration_seconds = models.IntegerField(default=0)
    file_size_mb = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Access control
    is_public = models.BooleanField(default=False, help_text="Allow non-enrolled students to view")

    # Stats
    view_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Recording: {self.title}"


class QAQuestion(models.Model):
    """Q&A questions during livestream"""
    stream = models.ForeignKey(LiveStream, on_delete=models.CASCADE, related_name='qa_questions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stream_questions')

    question = models.TextField()

    # Moderation
    is_answered = models.BooleanField(default=False)
    answer = models.TextField(blank=True)
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='answered_questions'
    )
    answered_at = models.DateTimeField(null=True, blank=True)

    # Engagement
    upvotes = models.IntegerField(default=0)
    is_pinned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-upvotes', '-created_at']
        indexes = [
            models.Index(fields=['stream', '-upvotes']),
        ]

    def __str__(self):
        return f"Q: {self.question[:50]}"


class QuestionUpvote(models.Model):
    """Track upvotes on Q&A questions"""
    question = models.ForeignKey(QAQuestion, on_delete=models.CASCADE, related_name='upvote_records')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['question', 'user']

    def __str__(self):
        return f"{self.user.username} upvoted question {self.question.id}"


class StreamChat(models.Model):
    """Chat messages during livestream (separate from main chat)"""
    stream = models.ForeignKey(LiveStream, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    message = models.TextField()

    # Moderation
    is_deleted = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['stream', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"


class VideoConference(models.Model):
    """
    Video conferencing sessions using Jitsi Meet.
    Can be linked to courses for office hours, group meetings, etc.
    """
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live'),
        ('ENDED', 'Ended'),
        ('CANCELLED', 'Cancelled'),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='video_conferences',
        null=True,
        blank=True,
        help_text="Optional: link to a course"
    )
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hosted_conferences',
        help_text="Meeting host (instructor or student)"
    )

    title = models.CharField(max_length=200, help_text="Meeting title")
    description = models.TextField(blank=True, help_text="Meeting description/agenda")

    # Jitsi room details
    room_name = models.CharField(
        max_length=200,
        unique=True,
        editable=False,
        help_text="Unique Jitsi room identifier"
    )

    # Schedule
    scheduled_start = models.DateTimeField(help_text="Scheduled start time")
    scheduled_end = models.DateTimeField(help_text="Scheduled end time")
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SCHEDULED'
    )

    # Settings
    require_password = models.BooleanField(
        default=False,
        help_text="Require password to join"
    )
    password = models.CharField(
        max_length=50,
        blank=True,
        help_text="Meeting password (if required)"
    )
    enable_recording = models.BooleanField(
        default=False,
        help_text="Allow meeting recording"
    )
    enable_lobby = models.BooleanField(
        default=False,
        help_text="Participants wait in lobby for host approval"
    )
    max_participants = models.IntegerField(
        default=50,
        help_text="Maximum number of participants"
    )

    # Restrictions
    restrict_to_course = models.BooleanField(
        default=True,
        help_text="Only enrolled students can join (if linked to course)"
    )

    # Recording
    recording_url = models.URLField(blank=True, help_text="Recording URL after meeting ends")

    # Stats
    total_participants = models.IntegerField(default=0)
    peak_participants = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=0, help_text="Actual meeting duration")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Video Conference'
        verbose_name_plural = 'Video Conferences'
        ordering = ['-scheduled_start']
        indexes = [
            models.Index(fields=['course', '-scheduled_start']),
            models.Index(fields=['host', '-scheduled_start']),
            models.Index(fields=['status', '-scheduled_start']),
        ]

    def __str__(self):
        return f"{self.title} - {self.scheduled_start.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        """Generate unique room name if not set."""
        if not self.room_name:
            import uuid
            self.room_name = f"usiu-lms-{uuid.uuid4().hex[:12]}"
        super().save(*args, **kwargs)

    @property
    def is_live(self):
        """Check if conference is currently live."""
        return self.status == 'LIVE'

    @property
    def is_upcoming(self):
        """Check if conference is scheduled for future."""
        from django.utils import timezone
        return self.status == 'SCHEDULED' and self.scheduled_start > timezone.now()

    @property
    def jitsi_url(self):
        """Generate Jitsi Meet URL for this conference."""
        return f"https://meet.jit.si/{self.room_name}"

    def can_join(self, user):
        """Check if a user can join this conference."""
        # Host can always join
        if user == self.host:
            return True

        # Check if meeting is live or scheduled
        if self.status not in ['SCHEDULED', 'LIVE']:
            return False

        # If restricted to course, check enrollment
        if self.restrict_to_course and self.course:
            from djangolms.courses.models import Enrollment
            return Enrollment.objects.filter(
                student=user,
                course=self.course,
                status='ENROLLED'
            ).exists()

        # Otherwise, anyone can join
        return True


class VideoConferenceParticipant(models.Model):
    """
    Track participants who join video conferences.
    """
    conference = models.ForeignKey(
        VideoConference,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conference_participations'
    )

    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(
        default=0,
        help_text="Time spent in conference (minutes)"
    )

    # Engagement
    camera_on = models.BooleanField(default=True)
    microphone_on = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Conference Participant'
        verbose_name_plural = 'Conference Participants'
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['conference', '-joined_at']),
            models.Index(fields=['user', '-joined_at']),
        ]

    def __str__(self):
        return f"{self.user.username} in {self.conference.title}"
