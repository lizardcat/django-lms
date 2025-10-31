from django.contrib import admin
from django.utils.html import format_html
from .models import GradeScale, GradeCategory, CourseGrade, GradeHistory


@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    """
    Admin interface for GradeScale model.
    """
    list_display = ['course', 'a_min', 'b_min', 'c_min', 'd_min', 'use_plus_minus', 'updated_at']
    list_filter = ['use_plus_minus', 'created_at']
    search_fields = ['course__code', 'course__title']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Course', {
            'fields': ('course',)
        }),
        ('Grade Thresholds', {
            'fields': ('a_min', 'b_min', 'c_min', 'd_min'),
            'description': 'Set minimum percentages for each letter grade.'
        }),
        ('Options', {
            'fields': ('use_plus_minus',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GradeCategory)
class GradeCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for GradeCategory model.
    """
    list_display = ['name', 'course', 'assignment_type', 'weight', 'drop_lowest', 'created_at']
    list_filter = ['assignment_type', 'course']
    search_fields = ['name', 'course__code', 'course__title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['course', '-weight']

    fieldsets = (
        ('Category Information', {
            'fields': ('course', 'name', 'assignment_type')
        }),
        ('Weighting', {
            'fields': ('weight', 'drop_lowest'),
            'description': 'Weight must be expressed as percentage (0-100). Drop lowest determines how many lowest scores to ignore.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class GradeHistoryInline(admin.TabularInline):
    """
    Inline admin for grade history.
    """
    model = GradeHistory
    extra = 0
    readonly_fields = ['changed_by', 'change_type', 'old_percentage', 'new_percentage', 'old_letter', 'new_letter', 'reason', 'timestamp']
    can_delete = False
    max_num = 10

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CourseGrade)
class CourseGradeAdmin(admin.ModelAdmin):
    """
    Admin interface for CourseGrade model.
    """
    list_display = ['get_student', 'get_course', 'display_grade', 'letter_grade', 'is_overridden_display', 'last_calculated']
    list_filter = ['is_overridden', 'letter_grade', 'enrollment__course', 'last_calculated']
    search_fields = ['enrollment__student__username', 'enrollment__student__email', 'enrollment__course__code']
    readonly_fields = ['enrollment', 'percentage', 'letter_grade', 'last_calculated', 'created_at']
    inlines = [GradeHistoryInline]
    ordering = ['-last_calculated']

    fieldsets = (
        ('Enrollment', {
            'fields': ('enrollment',)
        }),
        ('Calculated Grade', {
            'fields': ('percentage', 'letter_grade', 'last_calculated'),
            'description': 'These fields are automatically calculated based on assignment grades.'
        }),
        ('Manual Override', {
            'fields': ('is_overridden', 'override_percentage', 'override_letter', 'override_reason', 'overridden_by', 'overridden_at'),
            'classes': ('collapse',),
            'description': 'Manually override the calculated grade if necessary.'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_student(self, obj):
        return obj.enrollment.student.get_full_name() or obj.enrollment.student.username
    get_student.short_description = 'Student'
    get_student.admin_order_field = 'enrollment__student__last_name'

    def get_course(self, obj):
        return obj.enrollment.course.code
    get_course.short_description = 'Course'
    get_course.admin_order_field = 'enrollment__course__code'

    def display_grade(self, obj):
        percentage = obj.get_display_percentage()
        if percentage:
            return f"{percentage}%"
        return "N/A"
    display_grade.short_description = 'Grade'

    def is_overridden_display(self, obj):
        if obj.is_overridden:
            return format_html('<span style="color: orange;">✓ Overridden</span>')
        return format_html('<span style="color: green;">✗ Calculated</span>')
    is_overridden_display.short_description = 'Status'

    actions = ['recalculate_grades']

    def recalculate_grades(self, request, queryset):
        count = 0
        for grade in queryset:
            if not grade.is_overridden:
                grade.calculate_grade()
                count += 1
        self.message_user(request, f'Recalculated {count} grade(s).')
    recalculate_grades.short_description = 'Recalculate selected grades'


@admin.register(GradeHistory)
class GradeHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for GradeHistory model.
    """
    list_display = ['get_student', 'get_course', 'change_type', 'old_percentage', 'new_percentage', 'changed_by', 'timestamp']
    list_filter = ['change_type', 'timestamp']
    search_fields = ['course_grade__enrollment__student__username', 'course_grade__enrollment__course__code', 'reason']
    readonly_fields = ['course_grade', 'changed_by', 'change_type', 'old_percentage', 'new_percentage', 'old_letter', 'new_letter', 'reason', 'timestamp']
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_student(self, obj):
        return obj.course_grade.enrollment.student.username
    get_student.short_description = 'Student'

    def get_course(self, obj):
        return obj.course_grade.enrollment.course.code
    get_course.short_description = 'Course'
