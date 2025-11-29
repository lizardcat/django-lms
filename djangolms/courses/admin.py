from django.contrib import admin
from .models import Course, Enrollment, Module, Material, MaterialView


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


# Course Materials Admin

class MaterialInline(admin.TabularInline):
    """Inline admin for materials within module admin."""
    model = Material
    extra = 1
    fields = ['title', 'material_type', 'file', 'url', 'is_required', 'order']
    ordering = ['order']
    show_change_link = True


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    """Admin interface for Module model."""
    list_display = ['title', 'course', 'order', 'is_published', 'is_available', 'material_count', 'created_at']
    list_filter = ['is_published', 'course', 'created_at']
    search_fields = ['title', 'description', 'course__code', 'course__title']
    readonly_fields = ['created_at', 'updated_at', 'material_count', 'is_available']
    ordering = ['course', 'order']
    inlines = [MaterialInline]

    fieldsets = (
        ('Module Information', {
            'fields': ('course', 'title', 'description', 'order')
        }),
        ('Visibility Settings', {
            'fields': ('is_published', 'unlock_date', 'is_available')
        }),
        ('Metadata', {
            'fields': ('material_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    """Admin interface for Material model."""
    list_display = ['title', 'module', 'material_type', 'file_extension', 'file_size_display', 'is_required', 'view_count', 'created_at']
    list_filter = ['material_type', 'is_required', 'is_downloadable', 'module__course']
    search_fields = ['title', 'description', 'module__title', 'module__course__code']
    readonly_fields = ['created_at', 'updated_at', 'file_size', 'file_extension', 'file_size_display', 'view_count', 'uploaded_by']
    ordering = ['module', 'order']

    fieldsets = (
        ('Material Information', {
            'fields': ('module', 'title', 'description', 'material_type', 'order')
        }),
        ('Content', {
            'fields': ('file', 'url', 'embed_code')
        }),
        ('Settings', {
            'fields': ('is_required', 'is_downloadable')
        }),
        ('Metadata', {
            'fields': ('file_size', 'file_extension', 'file_size_display', 'view_count', 'uploaded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Set uploaded_by to current user."""
        if not change:  # Only set on creation
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MaterialView)
class MaterialViewAdmin(admin.ModelAdmin):
    """Admin interface for MaterialView model."""
    list_display = ['student', 'material', 'viewed_at', 'duration_display', 'completed']
    list_filter = ['completed', 'viewed_at', 'material__module__course']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'material__title']
    readonly_fields = ['viewed_at']
    ordering = ['-viewed_at']
    date_hierarchy = 'viewed_at'

    fieldsets = (
        ('View Information', {
            'fields': ('material', 'student', 'viewed_at')
        }),
        ('Activity Details', {
            'fields': ('duration_seconds', 'completed')
        }),
    )

    def duration_display(self, obj):
        """Display duration in human-readable format."""
        if not obj.duration_seconds:
            return 'N/A'
        minutes, seconds = divmod(obj.duration_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f'{hours}h {minutes}m {seconds}s'
        elif minutes > 0:
            return f'{minutes}m {seconds}s'
        return f'{seconds}s'
    duration_display.short_description = 'Duration'
