from django.contrib import admin
from .models import Course, Enrollment


class EnrollmentInline(admin.TabularInline):
    """
    Inline admin for enrollments within course admin.
    """
    model = Enrollment
    extra = 0
    readonly_fields = ['enrolled_at']
    fields = ['student', 'status', 'enrolled_at']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Admin interface for Course model.
    """
    list_display = ['code', 'title', 'instructor', 'status', 'enrolled_count', 'max_students', 'start_date', 'created_at']
    list_filter = ['status', 'start_date', 'created_at']
    search_fields = ['code', 'title', 'instructor__username', 'instructor__first_name', 'instructor__last_name']
    readonly_fields = ['created_at', 'updated_at', 'enrolled_count']
    ordering = ['-created_at']
    inlines = [EnrollmentInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'code', 'description', 'instructor', 'status')
        }),
        ('Course Details', {
            'fields': ('thumbnail', 'max_students', 'start_date', 'end_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """
    Admin interface for Enrollment model.
    """
    list_display = ['student', 'course', 'status', 'enrolled_at', 'completed_at']
    list_filter = ['status', 'enrolled_at', 'course']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'course__code', 'course__title']
    readonly_fields = ['enrolled_at']
    ordering = ['-enrolled_at']

    fieldsets = (
        ('Enrollment Information', {
            'fields': ('student', 'course', 'status')
        }),
        ('Dates', {
            'fields': ('enrolled_at', 'completed_at')
        }),
    )
