from django.db import models
from django.conf import settings
from django.utils import timezone


class Course(models.Model):
    """
    Course model representing a course in the LMS.
    """
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        ARCHIVED = 'ARCHIVED', 'Archived'

    title = models.CharField(max_length=200, help_text="Course title")
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique course code (e.g., CS101)"
    )
    description = models.TextField(help_text="Course description")
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_teaching',
        limit_choices_to={'role': 'INSTRUCTOR'},
        help_text="Course instructor"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        help_text="Course status"
    )
    thumbnail = models.ImageField(
        upload_to='course_thumbnails/',
        blank=True,
        null=True,
        help_text="Course thumbnail image"
    )
    max_students = models.PositiveIntegerField(
        default=30,
        help_text="Maximum number of students"
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        help_text="Course start date"
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text="Course end date"
    )

    # Class schedule (optional - for regular meeting times)
    class_time = models.TimeField(
        blank=True,
        null=True,
        help_text="Regular class meeting time (e.g., 10:00 AM)"
    )
    class_days = models.CharField(
        max_length=100,
        blank=True,
        help_text="Days of week (e.g., Mon, Wed, Fri)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.title}"

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    @property
    def is_full(self):
        return self.enrollments.filter(status='ENROLLED').count() >= self.max_students

    @property
    def enrolled_count(self):
        return self.enrollments.filter(status='ENROLLED').count()

    @property
    def is_active(self):
        """Check if course is currently active based on dates."""
        if not self.start_date or not self.end_date:
            return self.is_published
        today = timezone.now().date()
        return self.is_published and self.start_date <= today <= self.end_date


class Enrollment(models.Model):
    """
    Enrollment model representing student enrollment in courses.
    """
    class Status(models.TextChoices):
        ENROLLED = 'ENROLLED', 'Enrolled'
        COMPLETED = 'COMPLETED', 'Completed'
        DROPPED = 'DROPPED', 'Dropped'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'STUDENT'},
        help_text="Enrolled student"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="Course"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ENROLLED,
        help_text="Enrollment status"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        ordering = ['-enrolled_at']
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.code}"

    @property
    def is_active(self):
        return self.status == self.Status.ENROLLED


class Module(models.Model):
    """
    Module model for organizing course materials into sections/weeks/topics.
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules',
        help_text="Course this module belongs to"
    )
    title = models.CharField(
        max_length=200,
        help_text="Module title (e.g., 'Week 1: Introduction')"
    )
    description = models.TextField(
        blank=True,
        help_text="Module description"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order (lower numbers first)"
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Is this module visible to students?"
    )
    unlock_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional date when module becomes available"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
        ordering = ['course', 'order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.code} - {self.title}"

    @property
    def is_available(self):
        """Check if module is available to students."""
        if not self.is_published:
            return False
        if self.unlock_date:
            return timezone.now() >= self.unlock_date
        return True

    @property
    def material_count(self):
        """Count of materials in this module."""
        return self.materials.count()


class Material(models.Model):
    """
    Material model for course files, documents, videos, and links.
    """
    class MaterialType(models.TextChoices):
        FILE = 'FILE', 'File'
        VIDEO = 'VIDEO', 'Video'
        LINK = 'LINK', 'External Link'
        DOCUMENT = 'DOCUMENT', 'Document'
        PRESENTATION = 'PRESENTATION', 'Presentation'

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='materials',
        help_text="Module this material belongs to"
    )
    title = models.CharField(
        max_length=200,
        help_text="Material title"
    )
    description = models.TextField(
        blank=True,
        help_text="Material description"
    )
    material_type = models.CharField(
        max_length=20,
        choices=MaterialType.choices,
        default=MaterialType.FILE,
        help_text="Type of material"
    )

    # For uploaded files
    file = models.FileField(
        upload_to='course_materials/%Y/%m/',
        blank=True,
        null=True,
        help_text="Uploaded file (PDF, video, document, etc.)"
    )

    # For external links
    url = models.URLField(
        blank=True,
        max_length=500,
        help_text="External URL (for links and videos)"
    )

    # For embedded content
    embed_code = models.TextField(
        blank=True,
        help_text="Embed code for videos (YouTube, Vimeo, etc.)"
    )

    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order within module"
    )
    is_required = models.BooleanField(
        default=False,
        help_text="Is this material required for course completion?"
    )
    is_downloadable = models.BooleanField(
        default=True,
        help_text="Allow students to download this material?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_materials',
        help_text="User who uploaded this material"
    )

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'
        ordering = ['module', 'order']

    def __str__(self):
        return f"{self.module.course.code} - {self.title}"

    @property
    def file_extension(self):
        """Get file extension from filename."""
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return None

    @property
    def file_size_display(self):
        """Display file size in human-readable format."""
        if not self.file_size:
            return None

        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"

    @property
    def view_count(self):
        """Count of students who have viewed this material."""
        return self.views.values('student').distinct().count()

    def save(self, *args, **kwargs):
        """Override save to calculate file size."""
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class MaterialView(models.Model):
    """
    MaterialView model to track when students view/access materials.
    Used for progress tracking and analytics.
    """
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name='views',
        help_text="Material that was viewed"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='material_views',
        limit_choices_to={'role': 'STUDENT'},
        help_text="Student who viewed the material"
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="How long the student viewed the material (in seconds)"
    )
    completed = models.BooleanField(
        default=False,
        help_text="Did the student complete viewing this material?"
    )

    class Meta:
        verbose_name = 'Material View'
        verbose_name_plural = 'Material Views'
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['student', 'material']),
            models.Index(fields=['material', '-viewed_at']),
        ]

    def __str__(self):
        return f"{self.student.username} viewed {self.material.title}"
