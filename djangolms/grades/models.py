from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from djangolms.courses.models import Course, Enrollment
from djangolms.assignments.models import Assignment


class GradeScale(models.Model):
    """
    Defines letter grade scales for courses.
    """
    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name='grade_scale',
        help_text="Course this grade scale applies to"
    )
    a_min = models.DecimalField(
        max_digits=5, decimal_places=2, default=90.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum percentage for A grade"
    )
    b_min = models.DecimalField(
        max_digits=5, decimal_places=2, default=80.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum percentage for B grade"
    )
    c_min = models.DecimalField(
        max_digits=5, decimal_places=2, default=70.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum percentage for C grade"
    )
    d_min = models.DecimalField(
        max_digits=5, decimal_places=2, default=60.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum percentage for D grade"
    )
    use_plus_minus = models.BooleanField(
        default=False,
        help_text="Use +/- modifiers (A+, A, A-)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Grade Scale'
        verbose_name_plural = 'Grade Scales'

    def __str__(self):
        return f"Grade Scale for {self.course.code}"

    def get_letter_grade(self, percentage):
        """Convert percentage to letter grade."""
        if percentage is None:
            return 'N/A'

        percentage = float(percentage)

        if percentage >= float(self.a_min):
            base = 'A'
        elif percentage >= float(self.b_min):
            base = 'B'
        elif percentage >= float(self.c_min):
            base = 'C'
        elif percentage >= float(self.d_min):
            base = 'D'
        else:
            return 'F'

        if not self.use_plus_minus:
            return base

        # Add +/- modifiers
        if base == 'A':
            if percentage >= 97:
                return 'A+'
            elif percentage >= float(self.a_min):
                return 'A' if percentage >= 93 else 'A-'
        else:
            # For B, C, D
            min_val = float(getattr(self, f'{base.lower()}_min'))
            next_min = float(self.a_min) if base == 'B' else float(getattr(self, f'{chr(ord(base) - 1).lower()}_min'))
            range_size = next_min - min_val

            if percentage >= min_val + (range_size * 0.7):
                return f'{base}+'
            elif percentage >= min_val + (range_size * 0.3):
                return base
            else:
                return f'{base}-'

        return base


class GradeCategory(models.Model):
    """
    Defines categories of assignments for weighted grading.
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='grade_categories',
        help_text="Course this category belongs to"
    )
    name = models.CharField(max_length=100, help_text="Category name (e.g., Homework, Quizzes)")
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Weight as percentage of final grade"
    )
    drop_lowest = models.PositiveIntegerField(
        default=0,
        help_text="Number of lowest scores to drop"
    )
    assignment_type = models.CharField(
        max_length=20,
        help_text="Maps to Assignment.assignment_type"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Grade Category'
        verbose_name_plural = 'Grade Categories'
        unique_together = ['course', 'assignment_type']
        ordering = ['-weight']

    def __str__(self):
        return f"{self.course.code} - {self.name} ({self.weight}%)"


class CourseGrade(models.Model):
    """
    Stores calculated grades for students in courses.
    """
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='grade',
        help_text="Enrollment this grade is for"
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Calculated percentage grade"
    )
    letter_grade = models.CharField(
        max_length=3,
        blank=True,
        help_text="Letter grade (A, B+, C-, etc.)"
    )
    is_overridden = models.BooleanField(
        default=False,
        help_text="Has been manually overridden by instructor"
    )
    override_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Manual override percentage"
    )
    override_letter = models.CharField(
        max_length=3,
        blank=True,
        help_text="Manual override letter grade"
    )
    override_reason = models.TextField(
        blank=True,
        help_text="Reason for grade override"
    )
    overridden_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grade_overrides',
        help_text="Instructor who made the override"
    )
    overridden_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the override was made"
    )
    last_calculated = models.DateTimeField(
        auto_now=True,
        help_text="When grade was last calculated"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Course Grade'
        verbose_name_plural = 'Course Grades'
        ordering = ['-percentage']

    def __str__(self):
        student = self.enrollment.student
        course = self.enrollment.course
        grade = self.get_display_grade()
        return f"{student.username} - {course.code}: {grade}"

    def get_display_percentage(self):
        """Get the percentage to display (override or calculated)."""
        if self.is_overridden and self.override_percentage is not None:
            return self.override_percentage
        return self.percentage

    def get_display_letter(self):
        """Get the letter grade to display (override or calculated)."""
        if self.is_overridden and self.override_letter:
            return self.override_letter
        return self.letter_grade

    def get_display_grade(self):
        """Get formatted grade for display."""
        letter = self.get_display_letter()
        percentage = self.get_display_percentage()
        if percentage is not None:
            return f"{letter} ({percentage}%)"
        return "N/A"

    def calculate_grade(self):
        """
        Calculate the student's grade based on assignments and categories.
        """
        course = self.enrollment.course
        student = self.enrollment.student

        # Get grade categories for this course
        categories = GradeCategory.objects.filter(course=course)

        if not categories.exists():
            # No categories defined, calculate simple average
            self._calculate_simple_average()
            return

        # Check if weights sum to 100
        total_weight = sum(float(cat.weight) for cat in categories)
        if abs(total_weight - 100) > 0.01:
            # Weights don't sum to 100, use simple average
            self._calculate_simple_average()
            return

        # Calculate weighted grade
        weighted_sum = 0
        total_weight_applied = 0

        for category in categories:
            # Get assignments for this category
            assignments = Assignment.objects.filter(
                course=course,
                assignment_type=category.assignment_type
            )

            if not assignments.exists():
                continue

            # Get student's submissions for these assignments
            from djangolms.assignments.models import Submission
            submissions = Submission.objects.filter(
                assignment__in=assignments,
                student=student,
                graded=True
            ).select_related('assignment')

            if not submissions.exists():
                continue

            # Calculate category average
            scores = []
            for sub in submissions:
                if sub.score is not None:
                    percentage = (sub.score / sub.assignment.total_points) * 100
                    scores.append(percentage)

            if scores:
                # Drop lowest scores if configured
                if category.drop_lowest > 0 and len(scores) > category.drop_lowest:
                    scores.sort()
                    scores = scores[category.drop_lowest:]

                category_avg = sum(scores) / len(scores)
                weighted_sum += category_avg * (float(category.weight) / 100)
                total_weight_applied += float(category.weight)

        if total_weight_applied > 0:
            # Adjust for missing categories
            self.percentage = round(weighted_sum * (100 / total_weight_applied), 2)
        else:
            self.percentage = None

        # Calculate letter grade
        self._update_letter_grade()
        self.save()

    def _calculate_simple_average(self):
        """Calculate simple average of all graded assignments."""
        from djangolms.assignments.models import Submission

        submissions = Submission.objects.filter(
            assignment__course=self.enrollment.course,
            student=self.enrollment.student,
            graded=True
        ).select_related('assignment')

        if not submissions.exists():
            self.percentage = None
            self.letter_grade = 'N/A'
            self.save()
            return

        total_percentage = 0
        count = 0

        for sub in submissions:
            if sub.score is not None:
                percentage = (sub.score / sub.assignment.total_points) * 100
                total_percentage += percentage
                count += 1

        if count > 0:
            self.percentage = round(total_percentage / count, 2)
        else:
            self.percentage = None

        self._update_letter_grade()
        self.save()

    def _update_letter_grade(self):
        """Update letter grade based on percentage."""
        if self.percentage is None:
            self.letter_grade = 'N/A'
            return

        try:
            scale = GradeScale.objects.get(course=self.enrollment.course)
            self.letter_grade = scale.get_letter_grade(self.percentage)
        except GradeScale.DoesNotExist:
            # Use default scale
            if self.percentage >= 90:
                self.letter_grade = 'A'
            elif self.percentage >= 80:
                self.letter_grade = 'B'
            elif self.percentage >= 70:
                self.letter_grade = 'C'
            elif self.percentage >= 60:
                self.letter_grade = 'D'
            else:
                self.letter_grade = 'F'


class GradeHistory(models.Model):
    """
    Tracks changes to course grades for audit purposes.
    """
    course_grade = models.ForeignKey(
        CourseGrade,
        on_delete=models.CASCADE,
        related_name='history',
        help_text="Course grade this history entry is for"
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='grade_changes',
        help_text="User who made the change"
    )
    change_type = models.CharField(
        max_length=20,
        choices=[
            ('CALCULATED', 'Automatic Calculation'),
            ('OVERRIDE', 'Manual Override'),
            ('REMOVED', 'Override Removed'),
        ],
        help_text="Type of change"
    )
    old_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    new_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    old_letter = models.CharField(max_length=3, blank=True)
    new_letter = models.CharField(max_length=3, blank=True)
    reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Grade History'
        verbose_name_plural = 'Grade Histories'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.course_grade} - {self.change_type} at {self.timestamp}"
