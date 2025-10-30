from django.db import models
from django.conf import settings
from django.utils import timezone
from djangolms.courses.models import Course


class Assignment(models.Model):
    """
    Assignment model representing coursework for students to complete.
    """
    class AssignmentType(models.TextChoices):
        HOMEWORK = 'HOMEWORK', 'Homework'
        QUIZ = 'QUIZ', 'Quiz'
        PROJECT = 'PROJECT', 'Project'
        EXAM = 'EXAM', 'Exam'
        ESSAY = 'ESSAY', 'Essay'

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments',
        help_text="Course this assignment belongs to"
    )
    title = models.CharField(max_length=200, help_text="Assignment title")
    description = models.TextField(help_text="Assignment description and instructions")
    assignment_type = models.CharField(
        max_length=20,
        choices=AssignmentType.choices,
        default=AssignmentType.HOMEWORK,
        help_text="Type of assignment"
    )
    total_points = models.PositiveIntegerField(
        default=100,
        help_text="Maximum points for this assignment"
    )
    due_date = models.DateTimeField(help_text="Assignment due date")
    attachment = models.FileField(
        upload_to='assignment_files/',
        blank=True,
        null=True,
        help_text="Optional attachment (PDF, docs, etc.)"
    )
    allow_late_submission = models.BooleanField(
        default=False,
        help_text="Allow submissions after due date"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.course.code} - {self.title}"

    @property
    def is_overdue(self):
        """Check if assignment is past due date."""
        return timezone.now() > self.due_date

    @property
    def submission_count(self):
        """Count of submissions for this assignment."""
        return self.submissions.count()

    @property
    def graded_count(self):
        """Count of graded submissions."""
        return self.submissions.filter(graded=True).count()


class Submission(models.Model):
    """
    Submission model representing a student's submission for an assignment.
    """
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text="Assignment being submitted"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        limit_choices_to={'role': 'STUDENT'},
        help_text="Student making the submission"
    )
    submission_text = models.TextField(
        blank=True,
        help_text="Text submission content"
    )
    attachment = models.FileField(
        upload_to='submission_files/',
        blank=True,
        null=True,
        help_text="Submitted file"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Grading
    graded = models.BooleanField(default=False, help_text="Has been graded")
    score = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Points earned"
    )
    feedback = models.TextField(
        blank=True,
        help_text="Instructor feedback"
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions',
        help_text="Instructor who graded this submission"
    )
    graded_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When submission was graded"
    )

    class Meta:
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        ordering = ['-submitted_at']
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

    @property
    def is_late(self):
        """Check if submission was submitted after due date."""
        return self.submitted_at > self.assignment.due_date

    @property
    def percentage(self):
        """Calculate percentage score."""
        if self.graded and self.score is not None:
            return round((self.score / self.assignment.total_points) * 100, 2)
        return None
