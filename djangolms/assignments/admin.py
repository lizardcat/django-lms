from django.contrib import admin
from .models import Assignment, Submission


class SubmissionInline(admin.TabularInline):
    """
    Inline admin for submissions within assignment admin.
    """
    model = Submission
    extra = 0
    readonly_fields = ['student', 'submitted_at', 'is_late']
    fields = ['student', 'submitted_at', 'graded', 'score', 'is_late']
    can_delete = False


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """
    Admin interface for Assignment model.
    """
    list_display = ['title', 'course', 'assignment_type', 'total_points', 'due_date', 'submission_count', 'created_at']
    list_filter = ['assignment_type', 'course', 'due_date', 'allow_late_submission']
    search_fields = ['title', 'description', 'course__code', 'course__title']
    readonly_fields = ['created_at', 'updated_at', 'submission_count', 'graded_count']
    ordering = ['-due_date']
    inlines = [SubmissionInline]

    fieldsets = (
        ('Assignment Information', {
            'fields': ('course', 'title', 'description', 'assignment_type')
        }),
        ('Grading', {
            'fields': ('total_points', 'due_date', 'allow_late_submission')
        }),
        ('Attachments', {
            'fields': ('attachment',)
        }),
        ('Statistics', {
            'fields': ('submission_count', 'graded_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """
    Admin interface for Submission model.
    """
    list_display = ['student', 'assignment', 'submitted_at', 'is_late', 'graded', 'score', 'percentage']
    list_filter = ['graded', 'submitted_at', 'assignment__course']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'assignment__title']
    readonly_fields = ['submitted_at', 'updated_at', 'is_late', 'percentage']
    ordering = ['-submitted_at']

    fieldsets = (
        ('Submission Information', {
            'fields': ('assignment', 'student', 'submitted_at', 'updated_at', 'is_late')
        }),
        ('Submission Content', {
            'fields': ('submission_text', 'attachment')
        }),
        ('Grading', {
            'fields': ('graded', 'score', 'percentage', 'feedback', 'graded_by', 'graded_at')
        }),
    )
