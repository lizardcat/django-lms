from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta


def home_view(request):
    """
    Blackboard-style dashboard home page view.
    """
    context = {}

    if request.user.is_authenticated:
        from djangolms.courses.models import Course, Enrollment
        from djangolms.assignments.models import Assignment
        from djangolms.notifications.models import Notification

        # Get user's enrolled courses
        if request.user.is_student:
            enrollments = Enrollment.objects.filter(
                student=request.user,
                status='ENROLLED'
            ).select_related('course', 'course__instructor')
            my_courses = [enrollment.course for enrollment in enrollments]
        elif request.user.is_instructor:
            my_courses = Course.objects.filter(
                instructor=request.user,
                status='PUBLISHED'
            )
        else:
            my_courses = []

        # Get upcoming assignments (next 7 days)
        upcoming_assignments = []
        if request.user.is_student:
            enrolled_course_ids = [course.id for course in my_courses]
            upcoming_assignments = Assignment.objects.filter(
                course_id__in=enrolled_course_ids,
                due_date__gte=timezone.now(),
                due_date__lte=timezone.now() + timedelta(days=7)
            ).select_related('course').order_by('due_date')[:5]

        # Get recent notifications
        recent_notifications = Notification.objects.filter(
            recipient=request.user
        ).select_related('related_course')[:5]

        # Get unread notification count
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

        context = {
            'my_courses': my_courses,
            'upcoming_assignments': upcoming_assignments,
            'recent_notifications': recent_notifications,
            'unread_count': unread_count,
        }

    return render(request, 'home.html', context)
