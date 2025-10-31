from django import forms
from django.utils import timezone
from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    """Form for creating and editing course announcements."""

    class Meta:
        model = Announcement
        fields = ['title', 'content', 'priority', 'pinned', 'publish_at']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter announcement title',
                'style': 'width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;'
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Enter announcement content...',
                'rows': 8,
                'style': 'width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;'
            }),
            'priority': forms.Select(attrs={
                'style': 'width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;'
            }),
            'publish_at': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'style': 'width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;'
            }),
        }
        help_texts = {
            'pinned': 'Pinned announcements stay at the top of the list',
            'publish_at': 'Leave blank to publish immediately, or schedule for future',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default publish_at to now if not editing
        if not self.instance.pk and 'publish_at' not in self.initial:
            self.initial['publish_at'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

    def clean_publish_at(self):
        """Validate publish_at is not too far in the past."""
        publish_at = self.cleaned_data.get('publish_at')
        if publish_at:
            # Allow some time for timezone differences, but not more than 1 hour in past
            if publish_at < timezone.now() - timezone.timedelta(hours=1):
                raise forms.ValidationError(
                    'Publish time cannot be more than 1 hour in the past.'
                )
        return publish_at


class AnnouncementFilterForm(forms.Form):
    """Form for filtering announcements."""

    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + Announcement.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'style': 'padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;'
        })
    )
    pinned_only = forms.BooleanField(
        required=False,
        label='Pinned Only',
        widget=forms.CheckboxInput(attrs={
            'style': 'width: 1.25rem; height: 1.25rem;'
        })
    )
