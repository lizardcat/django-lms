from django import forms
from .models import Course


class CourseForm(forms.ModelForm):
    """
    Form for creating and editing courses.
    """
    class Meta:
        model = Course
        fields = ['title', 'code', 'description', 'thumbnail', 'max_students', 'start_date', 'end_date', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
