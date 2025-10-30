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
