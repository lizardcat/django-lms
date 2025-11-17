from django.contrib import admin
from .models import AIInteraction, AIGradingSuggestion, StudentAnalytics, QuizAssistanceSession


@admin.register(AIInteraction)
class AIInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'interaction_type', 'course', 'assignment', 'created_at', 'tokens_used', 'helpful')
    list_filter = ('interaction_type', 'created_at', 'helpful')
    search_fields = ('user__username', 'user__email', 'user_input', 'ai_response')
    readonly_fields = ('created_at', 'tokens_used', 'response_time_ms', 'model_used')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Context', {
            'fields': ('user', 'interaction_type', 'course', 'assignment', 'submission')
        }),
        ('Interaction', {
            'fields': ('user_input', 'ai_response')
        }),
        ('Metadata', {
            'fields': ('model_used', 'tokens_used', 'response_time_ms', 'created_at')
        }),
        ('Feedback', {
            'fields': ('helpful', 'feedback_comment')
        }),
    )


@admin.register(AIGradingSuggestion)
class AIGradingSuggestionAdmin(admin.ModelAdmin):
    list_display = ('submission', 'suggested_score', 'confidence_score', 'requires_human_review', 'accepted', 'created_at')
    list_filter = ('requires_human_review', 'accepted', 'created_at')
    search_fields = ('submission__student__username', 'submission__assignment__title', 'feedback')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Submission', {
            'fields': ('submission',)
        }),
        ('AI Suggestion', {
            'fields': ('suggested_score', 'confidence_score', 'feedback', 'strengths', 'areas_for_improvement', 'rubric_scores')
        }),
        ('Review Flags', {
            'fields': ('requires_human_review', 'flagged_reason')
        }),
        ('Instructor Action', {
            'fields': ('accepted', 'instructor_notes', 'reviewed_by', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(StudentAnalytics)
class StudentAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'predicted_grade', 'risk_level', 'engagement_score', 'participation_trend', 'last_analyzed')
    list_filter = ('risk_level', 'participation_trend', 'last_analyzed')
    search_fields = ('student__username', 'student__email', 'course__title')
    readonly_fields = ('last_analyzed', 'created_at')

    fieldsets = (
        ('Student & Course', {
            'fields': ('student', 'course')
        }),
        ('Performance Metrics', {
            'fields': ('predicted_grade', 'risk_level', 'engagement_score', 'participation_trend')
        }),
        ('AI Analysis', {
            'fields': ('learning_gaps', 'strengths', 'recommendations', 'summary')
        }),
        ('Metadata', {
            'fields': ('analyzed_assignments_count', 'last_analyzed', 'created_at')
        }),
    )


@admin.register(QuizAssistanceSession)
class QuizAssistanceSessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'hints_requested', 'explanations_requested', 'session_start', 'session_end')
    list_filter = ('session_start', 'session_end')
    search_fields = ('student__username', 'assignment__title')
    readonly_fields = ('session_start',)
