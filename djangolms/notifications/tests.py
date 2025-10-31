from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from djangolms.accounts.models import User
from djangolms.courses.models import Course, Enrollment
from .models import Announcement, AnnouncementRead, Notification
from .forms import AnnouncementForm


class AnnouncementModelTests(TestCase):
    """Test cases for Announcement model."""

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

    def test_announcement_creation(self):
        """Test creating an announcement."""
        announcement = Announcement.objects.create(
            course=self.course,
            author=self.instructor,
            title='Test Announcement',
            content='This is a test announcement',
            priority='NORMAL'
        )
        self.assertEqual(announcement.title, 'Test Announcement')
        self.assertEqual(announcement.priority, 'NORMAL')
        self.assertFalse(announcement.pinned)

    def test_is_published(self):
        """Test is_published method."""
        # Published announcement
        published = Announcement.objects.create(
            course=self.course,
            author=self.instructor,
            title='Published',
            content='Content',
            publish_at=timezone.now() - timedelta(hours=1)
        )
        self.assertTrue(published.is_published())

        # Scheduled announcement
        scheduled = Announcement.objects.create(
            course=self.course,
            author=self.instructor,
            title='Scheduled',
            content='Content',
            publish_at=timezone.now() + timedelta(hours=1)
        )
        self.assertFalse(scheduled.is_published())

    def test_get_priority_color(self):
        """Test priority color mapping."""
        announcement = Announcement.objects.create(
            course=self.course,
            author=self.instructor,
            title='Test',
            content='Content',
            priority='URGENT'
        )
        self.assertEqual(announcement.get_priority_color(), '#e74c3c')


class AnnouncementReadTests(TestCase):
    """Test cases for AnnouncementRead model."""

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
        self.announcement = Announcement.objects.create(
            course=self.course,
            author=self.instructor,
            title='Test Announcement',
            content='Content'
        )

    def test_announcement_read_creation(self):
        """Test marking announcement as read."""
        read_record = AnnouncementRead.objects.create(
            announcement=self.announcement,
            user=self.student
        )
        self.assertEqual(read_record.announcement, self.announcement)
        self.assertEqual(read_record.user, self.student)
        self.assertIsNotNone(read_record.read_at)

    def test_unique_together(self):
        """Test that a user can only mark an announcement as read once."""
        AnnouncementRead.objects.create(
            announcement=self.announcement,
            user=self.student
        )
        # Attempting to create duplicate should fail
        with self.assertRaises(Exception):
            AnnouncementRead.objects.create(
                announcement=self.announcement,
                user=self.student
            )


class NotificationModelTests(TestCase):
    """Test cases for Notification model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            role='STUDENT'
        )

    def test_notification_creation(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type='ASSIGNMENT',
            title='New Assignment',
            message='A new assignment has been posted'
        )
        self.assertEqual(notification.recipient, self.user)
        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)

    def test_mark_as_read(self):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type='GRADE',
            title='Grade Posted',
            message='Your assignment has been graded'
        )
        self.assertFalse(notification.is_read)

        notification.mark_as_read()
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)

    def test_get_icon(self):
        """Test get_icon method."""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type='ANNOUNCEMENT',
            title='Test',
            message='Test'
        )
        self.assertEqual(notification.get_icon(), '📢')


class AnnouncementFormTests(TestCase):
    """Test cases for AnnouncementForm."""

    def test_valid_form(self):
        """Test valid announcement form."""
        form_data = {
            'title': 'Test Announcement',
            'content': 'This is a test announcement content.',
            'priority': 'NORMAL',
            'pinned': False,
            'publish_at': timezone.now().strftime('%Y-%m-%dT%H:%M')
        }
        form = AnnouncementForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_publish_at_validation(self):
        """Test that publish_at cannot be too far in the past."""
        form_data = {
            'title': 'Test',
            'content': 'Content',
            'priority': 'NORMAL',
            'publish_at': (timezone.now() - timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M')
        }
        form = AnnouncementForm(data=form_data)
        self.assertFalse(form.is_valid())


class AnnouncementViewTests(TestCase):
    """Test cases for announcement views."""

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

    def test_course_announcements_requires_access(self):
        """Test that only enrolled students and instructors can view announcements."""
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123',
            role='STUDENT'
        )
        self.client.login(username='other', password='testpass123')
        response = self.client.get(reverse('course_announcements', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_course_announcements_accessible_to_instructor(self):
        """Test that instructor can view announcements."""
        self.client.login(username='instructor', password='testpass123')
        response = self.client.get(reverse('course_announcements', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)

    def test_course_announcements_accessible_to_enrolled_student(self):
        """Test that enrolled student can view announcements."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('course_announcements', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)

    def test_create_announcement_requires_instructor(self):
        """Test that only instructors can create announcements."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('create_announcement', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_create_announcement_success(self):
        """Test successful announcement creation."""
        self.client.login(username='instructor', password='testpass123')
        response = self.client.post(reverse('create_announcement', args=[self.course.id]), {
            'title': 'New Announcement',
            'content': 'This is a new announcement',
            'priority': 'NORMAL',
            'pinned': False,
            'publish_at': timezone.now().strftime('%Y-%m-%dT%H:%M')
        })
        self.assertEqual(Announcement.objects.count(), 1)
        announcement = Announcement.objects.first()
        self.assertEqual(announcement.title, 'New Announcement')

    def test_announcement_detail_marks_as_read(self):
        """Test that viewing announcement marks it as read for students."""
        announcement = Announcement.objects.create(
            course=self.course,
            author=self.instructor,
            title='Test',
            content='Content'
        )
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('announcement_detail', args=[announcement.id]))
        self.assertEqual(response.status_code, 200)

        # Check that read record was created
        self.assertTrue(
            AnnouncementRead.objects.filter(
                announcement=announcement,
                user=self.student
            ).exists()
        )


class NotificationViewTests(TestCase):
    """Test cases for notification views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            role='STUDENT'
        )

    def test_notification_list_requires_login(self):
        """Test that notification list requires authentication."""
        response = self.client.get(reverse('notification_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_notification_list_accessible(self):
        """Test that authenticated user can view notifications."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('notification_list'))
        self.assertEqual(response.status_code, 200)

    def test_mark_notification_read(self):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type='SYSTEM',
            title='Test',
            message='Test message'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('mark_notification_read', args=[notification.id]))

        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_delete_notification(self):
        """Test deleting notification."""
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type='SYSTEM',
            title='Test',
            message='Test message'
        )
        self.client.login(username='testuser', password='testpass123')
        self.client.post(reverse('delete_notification', args=[notification.id]))

        self.assertEqual(Notification.objects.count(), 0)


class NotificationCreationTests(TestCase):
    """Test automatic notification creation."""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@test.com',
            password='testpass123',
            role='INSTRUCTOR'
        )
        self.student1 = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            password='testpass123',
            role='STUDENT'
        )
        self.student2 = User.objects.create_user(
            username='student2',
            email='student2@test.com',
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
        Enrollment.objects.create(
            student=self.student1,
            course=self.course,
            status='ENROLLED'
        )
        Enrollment.objects.create(
            student=self.student2,
            course=self.course,
            status='ENROLLED'
        )

    def test_announcement_creates_notifications(self):
        """Test that creating announcement creates notifications for enrolled students."""
        from .views import create_announcement_notifications

        announcement = Announcement.objects.create(
            course=self.course,
            author=self.instructor,
            title='Important Announcement',
            content='Please read this'
        )

        # Manually call the helper function
        create_announcement_notifications(announcement)

        # Should create 2 notifications (one for each enrolled student)
        self.assertEqual(Notification.objects.count(), 2)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.student1,
                notification_type='ANNOUNCEMENT'
            ).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.student2,
                notification_type='ANNOUNCEMENT'
            ).exists()
        )
