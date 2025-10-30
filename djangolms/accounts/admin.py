from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for the User model.
    """
    list_display = ['username', 'email', 'role', 'first_name', 'last_name', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('LMS Information', {
            'fields': ('role', 'bio', 'profile_picture', 'date_of_birth')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('LMS Information', {
            'fields': ('role', 'bio', 'profile_picture', 'date_of_birth')
        }),
    )
