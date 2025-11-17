from django.db import models
from django.conf import settings
from djangolms.assignments.models import Assignment, Submission
from djangolms.courses.models import Course


class AIInteraction(models.Model):
    """Track all AI interactions for analytics and auditing"""
    INTERACTION_TYPES = [
        ('QUIZ_HINT', 'Quiz Hint'),
        ('QUIZ_EXPLANATION', 'Quiz Explanation'),
        ('ANSWER_REVIEW', 'Answer Review'),
        ('CONCEPT_HELP', 'Concept Help'),
        ('GRADING_ASSIST', 'Grading Assistance'),
        ('FEEDBACK_GEN', 'Feedback Generation'),
        ('STUDENT_ANALYTICS', 'Student Analytics'),
        ('PERFORMANCE_PREDICT', 'Performance Prediction'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True, blank=True)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, null=True, blank=True)

    # Input/Output
    user_input = models.TextField()
    ai_response = models.TextField()

    # Metadata
    model_used = models.CharField(max_length=50, default='claude-3-5-sonnet-20241022')
    tokens_used = models.IntegerField(default=0)
    response_time_ms = models.IntegerField(default=0)

    # Feedback
    helpful = models.BooleanField(null=True, blank=True)
    feedback_comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['interaction_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_interaction_type_display()} - {self.created_at}"


class AIGradingSuggestion(models.Model):
    """Store AI-generated grading suggestions for instructor review"""
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='ai_suggestion')

    suggested_score = models.DecimalField(max_digits=5, decimal_places=2)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, help_text="AI confidence (0-100)")

    feedback = models.TextField()
    strengths = models.JSONField(default=list, help_text="List of identified strengths")
    areas_for_improvement = models.JSONField(default=list, help_text="List of areas to improve")

    # Rubric breakdown if applicable
    rubric_scores = models.JSONField(default=dict, blank=True, help_text="Breakdown by rubric criteria")

    # Flags
    requires_human_review = models.BooleanField(default=False)
    flagged_reason = models.TextField(blank=True, help_text="Why flagged for human review")

    # Instructor action
    accepted = models.BooleanField(null=True, blank=True)
    instructor_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"AI Suggestion for {self.submission.assignment.title} - {self.submission.student.username}"


class StudentAnalytics(models.Model):
    """AI-generated analytics for each student in a course"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_analytics')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    # Performance metrics
    predicted_grade = models.CharField(max_length=5, blank=True)
    risk_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
        ('CRITICAL', 'Critical Risk'),
    ], default='LOW')

    # AI analysis
    learning_gaps = models.JSONField(default=list, help_text="Identified knowledge gaps")
    strengths = models.JSONField(default=list, help_text="Student's strong areas")
    recommendations = models.JSONField(default=list, help_text="Recommended interventions")

    # Engagement metrics
    engagement_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="0-100 score")
    participation_trend = models.CharField(max_length=20, default='STABLE', choices=[
        ('IMPROVING', 'Improving'),
        ('STABLE', 'Stable'),
        ('DECLINING', 'Declining'),
    ])

    # Summary
    summary = models.TextField(help_text="AI-generated summary of student performance")

    # Metadata
    analyzed_assignments_count = models.IntegerField(default=0)
    last_analyzed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_analyzed']
        unique_together = ['student', 'course']
        verbose_name_plural = 'Student Analytics'

    def __str__(self):
        return f"{self.student.username} - {self.course.title} Analytics"


class QuizAssistanceSession(models.Model):
    """Track student quiz assistance sessions"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_sessions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    hints_requested = models.IntegerField(default=0)
    explanations_requested = models.IntegerField(default=0)

    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)

    # Track what was helpful
    helpful_interactions = models.JSONField(default=list)

    class Meta:
        ordering = ['-session_start']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title} Session"
