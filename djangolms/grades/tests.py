from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from djangolms.accounts.models import User
from djangolms.courses.models import Course, Enrollment
from djangolms.assignments.models import Assignment, Submission
from .models import GradeScale, GradeCategory, CourseGrade, GradeHistory
from .forms import GradeScaleForm, GradeCategoryForm, GradeOverrideForm


class GradeScaleModelTests(TestCase):
    """Test cases for GradeScale model."""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@test.com',
            password='testpass123',
            role='INSTRUCTOR'
        )
        self.course = Course.objects.create(
            title='Test Course',
            code='TEST101',
            description='Test Description',
            instructor=self.instructor,
            max_students=30
        )

    def test_grade_scale_creation(self):
        """Test creating a grade scale."""
        scale = GradeScale.objects.create(
            course=self.course,
            a_min=90,
            b_min=80,
            c_min=70,
            d_min=60
        )
        self.assertEqual(scale.course, self.course)
        self.assertEqual(scale.a_min, 90)

    def test_get_letter_grade_basic(self):
        """Test letter grade calculation without plus/minus."""
        scale = GradeScale.objects.create(
            course=self.course,
            a_min=90,
            b_min=80,
            c_min=70,
            d_min=60,
            use_plus_minus=False
        )
        self.assertEqual(scale.get_letter_grade(95), 'A')
        self.assertEqual(scale.get_letter_grade(85), 'B')
        self.assertEqual(scale.get_letter_grade(75), 'C')
        self.assertEqual(scale.get_letter_grade(65), 'D')
        self.assertEqual(scale.get_letter_grade(55), 'F')

    def test_get_letter_grade_with_plus_minus(self):
        """Test letter grade calculation with plus/minus."""
        scale = GradeScale.objects.create(
            course=self.course,
            a_min=90,
            b_min=80,
            c_min=70,
            d_min=60,
            use_plus_minus=True
        )
        self.assertEqual(scale.get_letter_grade(98), 'A+')
        self.assertEqual(scale.get_letter_grade(93), 'A')
        self.assertEqual(scale.get_letter_grade(90), 'A-')
        self.assertEqual(scale.get_letter_grade(87), 'B+')


class GradeCategoryModelTests(TestCase):
    """Test cases for GradeCategory model."""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@test.com',
            password='testpass123',
            role='INSTRUCTOR'
        )
        self.course = Course.objects.create(
            title='Test Course',
            code='TEST101',
            description='Test Description',
            instructor=self.instructor,
            max_students=30
        )

    def test_grade_category_creation(self):
        """Test creating a grade category."""
        category = GradeCategory.objects.create(
            course=self.course,
            name='Homework',
            weight=30,
            assignment_type='HOMEWORK',
            drop_lowest=1
        )
        self.assertEqual(category.name, 'Homework')
        self.assertEqual(category.weight, 30)
        self.assertEqual(category.drop_lowest, 1)


class CourseGradeCalculationTests(TestCase):
    """Test cases for grade calculation logic."""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@test.com',
            password='testpass123',
            role='INSTRUCTOR'
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123',
            role='STUDENT'
        )
        self.course = Course.objects.create(
            title='Test Course',
            code='TEST101',
            description='Test Description',
            instructor=self.instructor,
            max_students=30
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            status='ENROLLED'
        )

    def test_simple_average_calculation(self):
        """Test simple average when no categories defined."""
        # Create assignments
        a1 = Assignment.objects.create(
            course=self.course,
            title='Assignment 1',
            description='Test',
            assignment_type='HOMEWORK',
            total_points=100,
            due_date=timezone.now() + timedelta(days=7)
        )
        a2 = Assignment.objects.create(
            course=self.course,
            title='Assignment 2',
            description='Test',
            assignment_type='QUIZ',
            total_points=50,
            due_date=timezone.now() + timedelta(days=7)
        )

        # Create submissions
        Submission.objects.create(
            assignment=a1,
            student=self.student,
            submission_text='Test',
            graded=True,
            score=80
        )
        Submission.objects.create(
            assignment=a2,
            student=self.student,
            submission_text='Test',
            graded=True,
            score=40
        )

        # Calculate grade
        grade = CourseGrade.objects.create(enrollment=self.enrollment)
        grade.calculate_grade()

        # 80/100 = 80%, 40/50 = 80%, average = 80%
        self.assertEqual(grade.percentage, Decimal('80.00'))

    def test_weighted_grade_calculation(self):
        """Test weighted grade calculation with categories."""
        # Create categories
        GradeCategory.objects.create(
            course=self.course,
            name='Homework',
            weight=30,
            assignment_type='HOMEWORK'
        )
        GradeCategory.objects.create(
            course=self.course,
            name='Exams',
            weight=70,
            assignment_type='EXAM'
        )

        # Create assignments
        hw = Assignment.objects.create(
            course=self.course,
            title='Homework 1',
            description='Test',
            assignment_type='HOMEWORK',
            total_points=100,
            due_date=timezone.now() + timedelta(days=7)
        )
        exam = Assignment.objects.create(
            course=self.course,
            title='Exam 1',
            description='Test',
            assignment_type='EXAM',
            total_points=100,
            due_date=timezone.now() + timedelta(days=7)
        )

        # Create submissions
        Submission.objects.create(
            assignment=hw,
            student=self.student,
            submission_text='Test',
            graded=True,
            score=90
        )
        Submission.objects.create(
            assignment=exam,
            student=self.student,
            submission_text='Test',
            graded=True,
            score=80
        )

        # Calculate grade
        grade = CourseGrade.objects.create(enrollment=self.enrollment)
        grade.calculate_grade()

        # (90 * 0.30) + (80 * 0.70) = 27 + 56 = 83
        self.assertEqual(grade.percentage, Decimal('83.00'))

    def test_drop_lowest_scores(self):
        """Test dropping lowest scores in a category."""
        # Create category with drop_lowest=1
        GradeCategory.objects.create(
            course=self.course,
            name='Homework',
            weight=100,
            assignment_type='HOMEWORK',
            drop_lowest=1
        )

        # Create assignments
        for i in range(3):
            Assignment.objects.create(
                course=self.course,
                title=f'Homework {i+1}',
                description='Test',
                assignment_type='HOMEWORK',
                total_points=100,
                due_date=timezone.now() + timedelta(days=7)
            )

        assignments = Assignment.objects.filter(course=self.course)

        # Create submissions with scores: 90, 70, 80
        scores = [90, 70, 80]
        for assignment, score in zip(assignments, scores):
            Submission.objects.create(
                assignment=assignment,
                student=self.student,
                submission_text='Test',
                graded=True,
                score=score
            )

        # Calculate grade
        grade = CourseGrade.objects.create(enrollment=self.enrollment)
        grade.calculate_grade()

        # Should drop 70, average of 90 and 80 = 85
        self.assertEqual(grade.percentage, Decimal('85.00'))


class GradeOverrideTests(TestCase):
    """Test cases for grade override functionality."""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@test.com',
            password='testpass123',
            role='INSTRUCTOR'
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123',
            role='STUDENT'
        )
        self.course = Course.objects.create(
            title='Test Course',
            code='TEST101',
            description='Test Description',
            instructor=self.instructor,
            max_students=30
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            status='ENROLLED'
        )

    def test_grade_override(self):
        """Test manually overriding a grade."""
        grade = CourseGrade.objects.create(
            enrollment=self.enrollment,
            percentage=75,
            letter_grade='C'
        )

        # Override grade
        grade.is_overridden = True
        grade.override_percentage = 85
        grade.override_letter = 'B'
        grade.override_reason = 'Extra credit for participation'
        grade.overridden_by = self.instructor
        grade.overridden_at = timezone.now()
        grade.save()

        self.assertTrue(grade.is_overridden)
        self.assertEqual(grade.get_display_percentage(), Decimal('85'))
        self.assertEqual(grade.get_display_letter(), 'B')

    def test_grade_history_creation(self):
        """Test that grade history is created on override."""
        grade = CourseGrade.objects.create(
            enrollment=self.enrollment,
            percentage=75,
            letter_grade='C'
        )

        # Create history entry
        history = GradeHistory.objects.create(
            course_grade=grade,
            changed_by=self.instructor,
            change_type='OVERRIDE',
            old_percentage=75,
            new_percentage=85,
            old_letter='C',
            new_letter='B',
            reason='Extra credit'
        )

        self.assertEqual(history.course_grade, grade)
        self.assertEqual(history.change_type, 'OVERRIDE')


class GradeFormTests(TestCase):
    """Test cases for grade forms."""

    def test_grade_scale_form_validation(self):
        """Test grade scale form validation."""
        # Invalid: A min should be greater than B min
        form_data = {
            'a_min': 80,
            'b_min': 85,
            'c_min': 70,
            'd_min': 60,
            'use_plus_minus': False
        }
        form = GradeScaleForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_grade_category_form_valid(self):
        """Test valid grade category form."""
        form_data = {
            'name': 'Homework',
            'assignment_type': 'HOMEWORK',
            'weight': 30,
            'drop_lowest': 1
        }
        form = GradeCategoryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_grade_override_form_requires_reason(self):
        """Test that grade override form requires a reason."""
        form_data = {
            'override_percentage': 85,
            'override_letter': 'B',
            'override_reason': ''
        }
        form = GradeOverrideForm(data=form_data)
        self.assertFalse(form.is_valid())
        # The error is in non_field_errors because it's from clean() method
        self.assertTrue(form.non_field_errors())


class GradeViewTests(TestCase):
    """Test cases for grade views."""

    def setUp(self):
        self.client = Client()
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@test.com',
            password='testpass123',
            role='INSTRUCTOR'
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123',
            role='STUDENT'
        )
        self.course = Course.objects.create(
            title='Test Course',
            code='TEST101',
            description='Test Description',
            instructor=self.instructor,
            max_students=30
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            status='ENROLLED'
        )

    def test_gradebook_requires_instructor(self):
        """Test that gradebook is only accessible to instructor."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('course_gradebook', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_gradebook_accessible_to_instructor(self):
        """Test that instructor can access gradebook."""
        self.client.login(username='instructor', password='testpass123')
        response = self.client.get(reverse('course_gradebook', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gradebook')

    def test_student_can_view_own_grades(self):
        """Test that student can view their own grades."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('student_grades', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)

    def test_grade_configuration_requires_instructor(self):
        """Test that grade configuration requires instructor."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('grade_configuration', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_export_grades_creates_csv(self):
        """Test that export grades creates a CSV file."""
        self.client.login(username='instructor', password='testpass123')
        response = self.client.get(reverse('export_grades', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])


class GradeWorkflowTests(TestCase):
    """Test complete grade workflow."""

    def setUp(self):
        self.client = Client()
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@test.com',
            password='testpass123',
            role='INSTRUCTOR'
        )
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123',
            role='STUDENT'
        )
        self.course = Course.objects.create(
            title='Test Course',
            code='TEST101',
            description='Test Description',
            instructor=self.instructor,
            max_students=30
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            status='ENROLLED'
        )

    def test_complete_grading_workflow(self):
        """Test complete workflow from assignment to final grade."""
        # 1. Create assignment
        assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='Test',
            assignment_type='HOMEWORK',
            total_points=100,
            due_date=timezone.now() + timedelta(days=7)
        )

        # 2. Student submits
        submission = Submission.objects.create(
            assignment=assignment,
            student=self.student,
            submission_text='My submission'
        )

        # 3. Instructor grades
        submission.graded = True
        submission.score = 85
        submission.graded_by = self.instructor
        submission.graded_at = timezone.now()
        submission.save()

        # 4. Calculate course grade
        grade, created = CourseGrade.objects.get_or_create(enrollment=self.enrollment)
        grade.calculate_grade()

        # 5. Verify grade
        self.assertEqual(grade.percentage, Decimal('85.00'))
        self.assertIsNotNone(grade.letter_grade)

        # 6. Instructor overrides grade
        grade.is_overridden = True
        grade.override_percentage = 90
        grade.override_letter = 'A'
        grade.override_reason = 'Extra credit'
        grade.overridden_by = self.instructor
        grade.overridden_at = timezone.now()
        grade.save()

        # Create history
        GradeHistory.objects.create(
            course_grade=grade,
            changed_by=self.instructor,
            change_type='OVERRIDE',
            old_percentage=85,
            new_percentage=90,
            old_letter='B',
            new_letter='A',
            reason='Extra credit'
        )

        # 7. Verify override
        self.assertEqual(grade.get_display_percentage(), Decimal('90'))
        self.assertEqual(grade.get_display_letter(), 'A')
        self.assertEqual(grade.history.count(), 1)
