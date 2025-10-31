from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Exists, OuterRef
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse

from djangolms.courses.models import Course, Enrollment
from .models import Announcement, AnnouncementRead, Notification
from .forms import AnnouncementForm, AnnouncementFilterForm


# ==================== Announcement Views ====================

@login_required
def course_announcements(request, course_id):
    """View all announcements for a course."""
    course = get_object_or_404(Course, id=course_id)

    # Check if user has access (instructor or enrolled student)
    is_instructor = request.user == course.instructor
    is_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course,
        status='ENROLLED'
    ).exists()

    if not (is_instructor or is_enrolled):
        messages.error(request, 'You do not have access to this course.')
        return redirect('course_list')

    # Get announcements
    announcements = Announcement.objects.filter(
        course=course,
        publish_at__lte=timezone.now()
    ).select_related('author')

    # Apply filters if provided
    filter_form = AnnouncementFilterForm(request.GET)
    if filter_form.is_valid():
        priority = filter_form.cleaned_data.get('priority')
        pinned_only = filter_form.cleaned_data.get('pinned_only')

        if priority:
            announcements = announcements.filter(priority=priority)
        if pinned_only:
            announcements = announcements.filter(pinned=True)

    # Annotate with read status for current user
    if not is_instructor:
        announcements = announcements.annotate(
            is_read=Exists(
                AnnouncementRead.objects.filter(
                    announcement=OuterRef('pk'),
                    user=request.user
                )
            )
        )

    context = {
        'course': course,
        'announcements': announcements,
        'is_instructor': is_instructor,
        'filter_form': filter_form,
    }
    return render(request, 'notifications/course_announcements.html', context)


@login_required
def announcement_detail(request, announcement_id):
    """View a single announcement."""
    announcement = get_object_or_404(
        Announcement.objects.select_related('course', 'author'),
        id=announcement_id
    )
    course = announcement.course

    # Check access
    is_instructor = request.user == course.instructor
    is_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course,
        status='ENROLLED'
    ).exists()

    if not (is_instructor or is_enrolled):
        messages.error(request, 'You do not have access to this announcement.')
        return redirect('course_list')

    # Check if published
    if not announcement.is_published() and not is_instructor:
        messages.error(request, 'This announcement is not yet published.')
        return redirect('course_announcements', course_id=course.id)

    # Mark as read for students
    if not is_instructor:
        AnnouncementRead.objects.get_or_create(
            announcement=announcement,
            user=request.user
        )

    context = {
        'announcement': announcement,
        'course': course,
        'is_instructor': is_instructor,
    }
    return render(request, 'notifications/announcement_detail.html', context)


@login_required
def create_announcement(request, course_id):
    """Create a new announcement (instructors only)."""
    course = get_object_or_404(Course, id=course_id)

    # Only instructors can create announcements
    if request.user != course.instructor:
        messages.error(request, 'Only instructors can create announcements.')
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.course = course
            announcement.author = request.user
            announcement.save()

            # Create notifications for enrolled students
            create_announcement_notifications(announcement)

            messages.success(request, 'Announcement created successfully!')
            return redirect('announcement_detail', announcement_id=announcement.id)
    else:
        form = AnnouncementForm()

    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'notifications/announcement_form.html', context)


@login_required
def edit_announcement(request, announcement_id):
    """Edit an existing announcement (instructors only)."""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    course = announcement.course

    # Only course instructor can edit
    if request.user != course.instructor:
        messages.error(request, 'Only instructors can edit announcements.')
        return redirect('announcement_detail', announcement_id=announcement.id)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully!')
            return redirect('announcement_detail', announcement_id=announcement.id)
    else:
        form = AnnouncementForm(instance=announcement)

    context = {
        'form': form,
        'announcement': announcement,
        'course': course,
    }
    return render(request, 'notifications/announcement_form.html', context)


@login_required
def delete_announcement(request, announcement_id):
    """Delete an announcement (instructors only)."""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    course = announcement.course

    # Only course instructor can delete
    if request.user != course.instructor:
        messages.error(request, 'Only instructors can delete announcements.')
        return redirect('announcement_detail', announcement_id=announcement.id)

    if request.method == 'POST':
        course_id = course.id
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully.')
        return redirect('course_announcements', course_id=course_id)

    context = {
        'announcement': announcement,
        'course': course,
    }
    return render(request, 'notifications/announcement_confirm_delete.html', context)


# ==================== Notification Views ====================

@login_required
def notification_list(request):
    """View all notifications for current user."""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('related_course', 'related_announcement')

    # Filter by type if specified
    notification_type = request.GET.get('type')
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)

    # Filter by read/unread
    status = request.GET.get('status')
    if status == 'unread':
        notifications = notifications.filter(is_read=False)
    elif status == 'read':
        notifications = notifications.filter(is_read=True)

    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'notification_types': Notification.NOTIFICATION_TYPES,
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )
    notification.mark_as_read()

    # Redirect to action URL if available, otherwise back to notifications
    if notification.action_url:
        return redirect(notification.action_url)
    return redirect('notification_list')


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read."""
    if request.method == 'POST':
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        messages.success(request, 'All notifications marked as read.')

    return redirect('notification_list')


@login_required
def delete_notification(request, notification_id):
    """Delete a notification."""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    if request.method == 'POST':
        notification.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        messages.success(request, 'Notification deleted.')
        return redirect('notification_list')

    return redirect('notification_list')


@login_required
def clear_all_notifications(request):
    """Clear all read notifications."""
    if request.method == 'POST':
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=True
        ).delete()[0]
        messages.success(request, f'Cleared {count} notification(s).')

    return redirect('notification_list')


# ==================== Helper Functions ====================

def create_announcement_notifications(announcement):
    """Create notifications for all enrolled students when announcement is posted."""
    if not announcement.is_published():
        # Don't create notifications for scheduled announcements yet
        return

    # Get all enrolled students
    enrollments = Enrollment.objects.filter(
        course=announcement.course,
        status='ENROLLED'
    ).select_related('student')

    # Create notification for each student
    notifications = []
    for enrollment in enrollments:
        notification = Notification(
            recipient=enrollment.student,
            notification_type='ANNOUNCEMENT',
            title=f'New announcement in {announcement.course.code}',
            message=f'{announcement.title}',
            related_course=announcement.course,
            related_announcement=announcement,
            action_url=reverse('announcement_detail', args=[announcement.id])
        )
        notifications.append(notification)

    # Bulk create for efficiency
    if notifications:
        Notification.objects.bulk_create(notifications)
