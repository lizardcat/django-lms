from django.contrib import admin
from .models import (
    Assignment, Submission, Quiz, Question,
    QuestionChoice, QuizAttempt, QuizResponse
)


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


# Quiz Admin

class QuestionChoiceInline(admin.TabularInline):
    """Inline admin for question choices."""
    model = QuestionChoice
    extra = 2
    fields = ['choice_text', 'is_correct', 'order']
    ordering = ['order']


class QuestionInline(admin.TabularInline):
    """Inline admin for questions within quiz admin."""
    model = Question
    extra = 1
    fields = ['question_text', 'question_type', 'points', 'order']
    ordering = ['order']
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin interface for Quiz model."""
    list_display = ['assignment', 'question_count', 'time_limit', 'allow_multiple_attempts', 'pass_percentage']
    list_filter = ['allow_multiple_attempts', 'show_correct_answers', 'randomize_questions']
    search_fields = ['assignment__title', 'assignment__course__code']
    readonly_fields = ['question_count', 'total_points']
    inlines = [QuestionInline]

    fieldsets = (
        ('Quiz Settings', {
            'fields': ('assignment', 'time_limit', 'pass_percentage')
        }),
        ('Attempt Settings', {
            'fields': ('allow_multiple_attempts', 'max_attempts')
        }),
        ('Display Settings', {
            'fields': ('show_correct_answers', 'randomize_questions')
        }),
        ('Statistics', {
            'fields': ('question_count', 'total_points'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin interface for Question model."""
    list_display = ['quiz', 'question_type', 'question_text_short', 'points', 'order']
    list_filter = ['question_type', 'quiz__assignment__course']
    search_fields = ['question_text', 'quiz__assignment__title']
    ordering = ['quiz', 'order']
    inlines = [QuestionChoiceInline]

    fieldsets = (
        ('Question Information', {
            'fields': ('quiz', 'question_text', 'question_type', 'points', 'order')
        }),
        ('Answer Explanation', {
            'fields': ('explanation',),
            'classes': ('collapse',)
        }),
    )

    def question_text_short(self, obj):
        """Display shortened question text."""
        return obj.question_text[:75] + '...' if len(obj.question_text) > 75 else obj.question_text
    question_text_short.short_description = 'Question'


@admin.register(QuestionChoice)
class QuestionChoiceAdmin(admin.ModelAdmin):
    """Admin interface for QuestionChoice model."""
    list_display = ['question_short', 'choice_text_short', 'is_correct', 'order']
    list_filter = ['is_correct', 'question__quiz']
    search_fields = ['choice_text', 'question__question_text']
    ordering = ['question', 'order']

    def question_short(self, obj):
        """Display shortened question text."""
        return obj.question.question_text[:50] + '...' if len(obj.question.question_text) > 50 else obj.question.question_text
    question_short.short_description = 'Question'

    def choice_text_short(self, obj):
        """Display shortened choice text."""
        return obj.choice_text[:75] + '...' if len(obj.choice_text) > 75 else obj.choice_text
    choice_text_short.short_description = 'Choice'


class QuizResponseInline(admin.TabularInline):
    """Inline admin for quiz responses within quiz attempt admin."""
    model = QuizResponse
    extra = 0
    readonly_fields = ['question', 'answer_text', 'is_correct', 'points_earned', 'answered_at']
    fields = ['question', 'answer_text', 'is_correct', 'points_earned']
    can_delete = False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    """Admin interface for QuizAttempt model."""
    list_display = ['student', 'quiz', 'attempt_number', 'score', 'total_points', 'percentage', 'passed', 'submitted_at']
    list_filter = ['passed', 'submitted_at', 'quiz__assignment__course']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'quiz__assignment__title']
    readonly_fields = ['started_at', 'submitted_at', 'score', 'total_points', 'percentage', 'is_complete']
    ordering = ['-started_at']
    inlines = [QuizResponseInline]

    fieldsets = (
        ('Attempt Information', {
            'fields': ('quiz', 'student', 'attempt_number', 'started_at', 'submitted_at', 'is_complete')
        }),
        ('Results', {
            'fields': ('score', 'total_points', 'percentage', 'passed')
        }),
    )

    actions = ['grade_selected_attempts']

    def grade_selected_attempts(self, request, queryset):
        """Admin action to grade selected quiz attempts."""
        graded_count = 0
        for attempt in queryset:
            if not attempt.is_complete:
                attempt.grade_quiz()
                graded_count += 1
        self.message_user(request, f'Successfully graded {graded_count} quiz attempts.')
    grade_selected_attempts.short_description = 'Grade selected quiz attempts'


@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    """Admin interface for QuizResponse model."""
    list_display = ['attempt', 'question_short', 'answer_text_short', 'is_correct', 'points_earned', 'answered_at']
    list_filter = ['is_correct', 'attempt__quiz']
    search_fields = ['attempt__student__username', 'question__question_text', 'answer_text']
    readonly_fields = ['answered_at']
    ordering = ['-answered_at']

    def question_short(self, obj):
        """Display shortened question text."""
        return obj.question.question_text[:50] + '...' if len(obj.question.question_text) > 50 else obj.question.question_text
    question_short.short_description = 'Question'

    def answer_text_short(self, obj):
        """Display shortened answer text."""
        return obj.answer_text[:75] + '...' if len(obj.answer_text) > 75 else obj.answer_text
    answer_text_short.short_description = 'Answer'
