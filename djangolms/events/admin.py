from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'course', 'start_date', 'created_by']
    list_filter = ['event_type', 'course', 'start_date', 'all_day']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'event_type', 'color')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'end_date', 'all_day')
        }),
        ('Relations', {
            'fields': ('course', 'created_by')
        }),
    )
