from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
from djangolms.accounts.models import User
from djangolms.courses.models import Course, Enrollment
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm, GradeSubmissionForm


class AssignmentModelTests(TestCase):
    """Test cases for Assignment model."""

    def setUp(self):
        """Set up test data."""
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
        self.future_date = timezone.now() + timedelta(days=7)
        self.past_date = timezone.now() - timedelta(days=7)

    def test_assignment_creation(self):
        """Test creating an assignment."""
        assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='Test Description',
            assignment_type='HOMEWORK',
            total_points=100,
            due_date=self.future_date
        )
        self.assertEqual(assignment.title, 'Test Assignment')
        self.assertEqual(assignment.course, self.course)
        self.assertFalse(assignment.is_overdue)

    def test_assignment_is_overdue(self):
        """Test is_overdue property."""
        assignment = Assignment.objects.create(
            course=self.course,
            title='Overdue Assignment',
            description='Test Description',
            assignment_type='HOMEWORK',
            total_points=100,
            due_date=self.past_date
        )
        self.assertTrue(assignment.is_overdue)

    def test_assignment_str_method(self):
        """Test string representation."""
        assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='Test Description',
            assignment_type='QUIZ',
            total_points=50,
            due_date=self.future_date
        )
        expected_str = f"{self.course.code} - {assignment.title}"
        self.assertEqual(str(assignment), expected_str)

    def test_submission_count_property(self):
        """Test submission_count property."""
        assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='Test Description',
            assignment_type='HOMEWORK',
            total_points=100,
            due_date=self.future_date
        )
        self.assertEqual(assignment.submission_count, 0)

        student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123',
            role='STUDENT'
        )
        Submission.objects.create(
            assignment=assignment,
            student=student,
            submission_text='Test submission'
        )
        self.assertEqual(assignment.submission_count, 1)


class SubmissionModelTests(TestCase):
    """Test cases for Submission model."""

    def setUp(self):
        """Set up test data."""
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
        self.future_date = timezone.now() + timedelta(days=7)
        self.past_date = timezone.now() - timedelta(days=7)
        self.assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='Test Description',
            assignment_type='HOMEWORK',
            total_points=100,
            due_date=self.past_date
        )

    def test_submission_creation(self):
        """Test creating a submission."""
        submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            submission_text='My submission'
        )
        self.assertEqual(submission.assignment, self.assignment)
        self.assertEqual(submission.student, self.student)
        self.assertFalse(submission.graded)

    def test_submission_is_late(self):
        """Test is_late property."""
        submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            submission_text='Late submission'
        )
        self.assertTrue(submission.is_late)

    def test_submission_percentage(self):
        """Test percentage calculation."""
        submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            submission_text='Test submission',
            graded=True,
            score=85
        )
        self.assertEqual(submission.percentage, 85.0)

    def test_submission_percentage_not_graded(self):
        """Test percentage returns None when not graded."""
        submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            submission_text='Test submission'
        )
        self.assertIsNone(submission.percentage)

    def test_unique_submission_per_student(self):
        """Test that a student can only submit once per assignment."""
        Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            submission_text='First submission'
        )
        with self.assertRaises(Exception):
            Submission.objects.create(
                assignment=self.assignment,
                student=self.student,
                submission_text='Second submission'
            )


class AssignmentFormTests(TestCase):
    """Test cases for AssignmentForm."""

    def test_valid_form(self):
        """Test form with valid data."""
        future_date = timezone.now() + timedelta(days=7)
        form_data = {
            'title': 'Test Assignment',
            'description': 'Test Description',
            'assignment_type': 'HOMEWORK',
            'total_points': 100,
            'due_date': future_date,
            'allow_late_submission': False
        }
        form = AssignmentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_past_due_date_invalid(self):
        """Test that past due date is invalid for new assignments."""
        past_date = timezone.now() - timedelta(days=1)
        form_data = {
            'title': 'Test Assignment',
            'description': 'Test Description',
            'assignment_type': 'HOMEWORK',
            'total_points': 100,
            'due_date': past_date,
            'allow_late_submission': False
        }
        form = AssignmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)

    def test_negative_total_points_invalid(self):
        """Test that negative total points is invalid."""
        future_date = timezone.now() + timedelta(days=7)
        form_data = {
            'title': 'Test Assignment',
            'description': 'Test Description',
            'assignment_type': 'HOMEWORK',
            'total_points': -10,
            'due_date': future_date,
            'allow_late_submission': False
        }
        form = AssignmentForm(data=form_data)
        self.assertFalse(form.is_valid())


class GradeSubmissionFormTests(TestCase):
    """Test cases for GradeSubmissionForm."""

    def setUp(self):
        """Set up test data."""
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
        self.assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='Test Description',
            assignment_type='HOMEWORK',
            total_points=100,
            due_date=timezone.now() + timedelta(days=7)
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            submission_text='Test submission'
        )

    def test_valid_score(self):
        """Test form with valid score."""
        form_data = {
            'score': 85,
            'feedback': 'Good work!'
        }
        form = GradeSubmissionForm(data=form_data, instance=self.submission)
        self.assertTrue(form.is_valid())

    def test_score_exceeds_total_points(self):
        """Test that score exceeding total points is invalid."""
        form_data = {
            'score': 150,
            'feedback': 'Feedback'
        }
        form = GradeSubmissionForm(data=form_data, instance=self.submission)
        self.assertFalse(form.is_valid())
        self.assertIn('score', form.errors)

    def test_negative_score_invalid(self):
        """Test that negative score is invalid."""
        form_data = {
            'score': -10,
            'feedback': 'Feedback'
        }
        form = GradeSubmissionForm(data=form_data, instance=self.submission)
        self.assertFalse(form.is_valid())
        self.assertIn('score', form.errors)


class AssignmentViewTests(TestCase):
    """Test cases for assignment views."""

    def setUp(self):
        """Set up test data."""
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
        self.assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='Test Description',
            assignment_type='HOMEWORK',
            total_points=100,
            due_date=timezone.now() + timedelta(days=7)
        )

    def test_assignment_list_requires_login(self):
        """Test that assignment list requires login."""
        response = self.client.get(reverse('assignment_list', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_assignment_list_as_student(self):
        """Test assignment list view as student."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('assignment_list', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.assignment.title)

    def test_assignment_list_as_instructor(self):
        """Test assignment list view as instructor."""
        self.client.login(username='instructor', password='testpass123')
        response = self.client.get(reverse('assignment_list', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Assignment')

    def test_assignment_detail_view(self):
        """Test assignment detail view."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('assignment_detail', args=[self.assignment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.assignment.title)
        self.assertContains(response, self.assignment.description)

    def test_assignment_create_as_instructor(self):
        """Test creating assignment as instructor."""
        self.client.login(username='instructor', password='testpass123')
        response = self.client.get(reverse('assignment_create', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)

    def test_assignment_create_as_student_denied(self):
        """Test that students cannot create assignments."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('assignment_create', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_submit_assignment_as_student(self):
        """Test submitting assignment as student."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('submit_assignment', args=[self.assignment.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_submissions_as_instructor(self):
        """Test viewing submissions as instructor."""
        self.client.login(username='instructor', password='testpass123')
        response = self.client.get(reverse('view_submissions', args=[self.assignment.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_submissions_as_student_denied(self):
        """Test that students cannot view all submissions."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('view_submissions', args=[self.assignment.id]))
        self.assertEqual(response.status_code, 302)  # Redirect


class SubmissionWorkflowTests(TestCase):
    """Test cases for complete submission workflow."""

    def setUp(self):
        """Set up test data."""
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
        self.assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='Test Description',
            assignment_type='HOMEWORK',
            total_points=100,
            due_date=timezone.now() + timedelta(days=7)
        )

    def test_complete_submission_and_grading_workflow(self):
        """Test the complete workflow from submission to grading."""
        # Student submits assignment
        self.client.login(username='student', password='testpass123')
        response = self.client.post(
            reverse('submit_assignment', args=[self.assignment.id]),
            {
                'submission_text': 'My test submission',
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Verify submission was created
        submission = Submission.objects.get(assignment=self.assignment, student=self.student)
        self.assertEqual(submission.submission_text, 'My test submission')
        self.assertFalse(submission.graded)

        # Instructor grades the submission
        self.client.login(username='instructor', password='testpass123')
        response = self.client.post(
            reverse('grade_submission', args=[submission.id]),
            {
                'score': 90,
                'feedback': 'Excellent work!'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Verify grading was recorded
        submission.refresh_from_db()
        self.assertTrue(submission.graded)
        self.assertEqual(submission.score, 90)
        self.assertEqual(submission.feedback, 'Excellent work!')
        self.assertEqual(submission.percentage, 90.0)
