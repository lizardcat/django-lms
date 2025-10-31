from django import forms
from django.core.exceptions import ValidationError
from .models import GradeScale, GradeCategory, CourseGrade, GradeHistory


class GradeScaleForm(forms.ModelForm):
    """
    Form for creating and editing grade scales.
    """
    class Meta:
        model = GradeScale
        fields = ['a_min', 'b_min', 'c_min', 'd_min', 'use_plus_minus']
        widgets = {
            'a_min': forms.NumberInput(attrs={'min': '0', 'max': '100', 'step': '0.01'}),
            'b_min': forms.NumberInput(attrs={'min': '0', 'max': '100', 'step': '0.01'}),
            'c_min': forms.NumberInput(attrs={'min': '0', 'max': '100', 'step': '0.01'}),
            'd_min': forms.NumberInput(attrs={'min': '0', 'max': '100', 'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        a_min = cleaned_data.get('a_min')
        b_min = cleaned_data.get('b_min')
        c_min = cleaned_data.get('c_min')
        d_min = cleaned_data.get('d_min')

        # Ensure grade thresholds are in descending order
        if a_min and b_min and a_min <= b_min:
            raise ValidationError('A minimum must be greater than B minimum.')
        if b_min and c_min and b_min <= c_min:
            raise ValidationError('B minimum must be greater than C minimum.')
        if c_min and d_min and c_min <= d_min:
            raise ValidationError('C minimum must be greater than D minimum.')

        return cleaned_data


class GradeCategoryForm(forms.ModelForm):
    """
    Form for creating and editing grade categories.
    """
    class Meta:
        model = GradeCategory
        fields = ['name', 'assignment_type', 'weight', 'drop_lowest']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Homework, Quizzes, Exams'}),
            'weight': forms.NumberInput(attrs={'min': '0', 'max': '100', 'step': '0.01'}),
            'drop_lowest': forms.NumberInput(attrs={'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set assignment_type choices from Assignment model
        from djangolms.assignments.models import Assignment
        self.fields['assignment_type'].widget = forms.Select(
            choices=Assignment.AssignmentType.choices
        )


class GradeOverrideForm(forms.ModelForm):
    """
    Form for manually overriding student grades.
    """
    class Meta:
        model = CourseGrade
        fields = ['override_percentage', 'override_letter', 'override_reason']
        widgets = {
            'override_percentage': forms.NumberInput(attrs={'min': '0', 'max': '100', 'step': '0.01'}),
            'override_letter': forms.TextInput(attrs={'maxlength': '3', 'placeholder': 'e.g., A, B+, C-'}),
            'override_reason': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reason for grade override...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        override_percentage = cleaned_data.get('override_percentage')
        override_letter = cleaned_data.get('override_letter')
        override_reason = cleaned_data.get('override_reason')

        # Require at least one: percentage or letter
        if not override_percentage and not override_letter:
            raise ValidationError('You must provide either an override percentage or letter grade.')

        # Require reason for override
        if not override_reason:
            raise ValidationError('You must provide a reason for the grade override.')

        return cleaned_data


class BulkRecalculateForm(forms.Form):
    """
    Form for bulk recalculating grades.
    """
    confirm = forms.BooleanField(
        required=True,
        label='I confirm that I want to recalculate all grades for this course'
    )

    notify_students = forms.BooleanField(
        required=False,
        initial=False,
        label='Send email notifications to students about grade updates'
    )
