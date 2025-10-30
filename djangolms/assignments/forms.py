from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
import os
from .models import Assignment, Submission

# Allowed file extensions for uploads
ALLOWED_ASSIGNMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt', '.zip', '.rar']
ALLOWED_SUBMISSION_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt', '.zip', '.rar', '.jpg', '.jpeg', '.png']
MAX_FILE_SIZE_MB = 10  # Maximum file size in MB


class AssignmentForm(forms.ModelForm):
    """
    Form for creating and editing assignments.
    """
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'assignment_type', 'total_points', 'due_date', 'attachment', 'allow_late_submission']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        # Only validate future date for new assignments
        if not self.instance.pk and due_date and due_date <= timezone.now():
            raise ValidationError('Due date must be in the future.')
        return due_date

    def clean_total_points(self):
        total_points = self.cleaned_data.get('total_points')
        if total_points and total_points <= 0:
            raise ValidationError('Total points must be greater than 0.')
        return total_points

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Check file size
            if attachment.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise ValidationError(f'File size cannot exceed {MAX_FILE_SIZE_MB}MB.')

            # Check file extension
            ext = os.path.splitext(attachment.name)[1].lower()
            if ext not in ALLOWED_ASSIGNMENT_EXTENSIONS:
                raise ValidationError(
                    f'Invalid file type. Allowed types: {", ".join(ALLOWED_ASSIGNMENT_EXTENSIONS)}'
                )
        return attachment


class SubmissionForm(forms.ModelForm):
    """
    Form for students to submit assignments.
    """
    class Meta:
        model = Submission
        fields = ['submission_text', 'attachment']
        widgets = {
            'submission_text': forms.Textarea(attrs={'rows': 10, 'placeholder': 'Enter your submission text here...'}),
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Check file size
            if attachment.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise ValidationError(f'File size cannot exceed {MAX_FILE_SIZE_MB}MB.')

            # Check file extension
            ext = os.path.splitext(attachment.name)[1].lower()
            if ext not in ALLOWED_SUBMISSION_EXTENSIONS:
                raise ValidationError(
                    f'Invalid file type. Allowed types: {", ".join(ALLOWED_SUBMISSION_EXTENSIONS)}'
                )
        return attachment

    def clean(self):
        cleaned_data = super().clean()
        submission_text = cleaned_data.get('submission_text')
        attachment = cleaned_data.get('attachment')

        # Require at least one: text or attachment
        if not submission_text and not attachment:
            raise ValidationError('You must provide either submission text or upload a file.')

        return cleaned_data


class GradeSubmissionForm(forms.ModelForm):
    """
    Form for instructors to grade submissions.
    """
    class Meta:
        model = Submission
        fields = ['score', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Provide feedback to the student...'}),
        }

    def clean_score(self):
        score = self.cleaned_data.get('score')
        if score is not None:
            if score < 0:
                raise ValidationError('Score cannot be negative.')
            if self.instance.assignment and score > self.instance.assignment.total_points:
                raise ValidationError(
                    f'Score cannot exceed {self.instance.assignment.total_points} points.'
                )
        return score
